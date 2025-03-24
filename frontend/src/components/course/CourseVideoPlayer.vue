<template>
  <div class="relative w-full aspect-video bg-slate-900 rounded-2xl overflow-hidden shadow-lg">
    <!-- Loading State -->
    <div
      v-if="loading"
      class="absolute inset-0 flex items-center justify-center bg-slate-900/90 z-10"
    >
      <div class="text-center">
        <div
          class="w-12 h-12 border-4 border-maroon-500 border-t-transparent rounded-full animate-spin mx-auto"
        ></div>
        <p class="mt-4 text-slate-200">Loading video... {{ videoUrl }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-if="error"
      class="absolute inset-0 flex items-center justify-center bg-slate-900/90 z-10"
    >
      <div class="text-center">
        <span class="material-symbols-outlined text-4xl text-red-500">error_outline</span>
        <p class="mt-2 text-slate-200">{{ error }}</p>
        <button
          @click="retryLoading"
          class="mt-4 px-4 py-2 bg-maroon-500 text-white rounded-lg hover:bg-maroon-600 transition-colors"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Video Player -->
    <video
      ref="videoPlayer"
      class="w-full h-full object-cover"
      :src="videoUrl"
      :poster="posterImage"
      @timeupdate="handleTimeUpdate"
      @ended="handleVideoEnd"
      @loadedmetadata="handleMetadataLoaded"
      @error="handleError"
      :controls="useNativeControls"
    >
      <source :src="videoUrl" type="video/mp4" />
      Your browser does not support the video tag.
    </video>

    <!-- Custom Controls (when not using native) -->
    <div
      v-if="!useNativeControls"
      class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-slate-900 to-transparent"
    >
      <div class="flex items-center space-x-4">
        <button @click="togglePlay" class="text-white hover:text-maroon-400 transition-colors">
          <span class="material-symbols-outlined text-2xl">
            {{ isPlaying ? 'pause' : 'play_arrow' }}
          </span>
        </button>

        <!-- Progress Bar -->
        <div class="relative flex-1 h-1 bg-slate-700 rounded-full cursor-pointer" @click="seek">
          <div
            class="absolute inset-y-0 left-0 bg-gradient-to-r from-maroon-500 to-maroon-600 rounded-full"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>

        <!-- Time Display -->
        <div class="text-sm text-slate-300 font-medium">
          {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
        </div>

        <!-- Volume Control -->
        <div class="flex items-center space-x-2">
          <button @click="toggleMute" class="text-white hover:text-maroon-400 transition-colors">
            <span class="material-symbols-outlined">
              {{ isMuted ? 'volume_off' : 'volume_up' }}
            </span>
          </button>
          <input
            type="range"
            v-model="volume"
            min="0"
            max="1"
            step="0.1"
            class="w-20 accent-maroon-500"
          />
        </div>

        <!-- Fullscreen Toggle -->
        <button
          @click="toggleFullscreen"
          class="text-white hover:text-maroon-400 transition-colors"
        >
          <span class="material-symbols-outlined">
            {{ isFullscreen ? 'fullscreen_exit' : 'fullscreen' }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { VuePlayer } from '@display-studio/vue-player'
import { useNotification } from '@/composables/useNotification'

const VIDEO_CACHE_PREFIX = 'video_cache_'
const CACHE_DURATION = 24 * 60 * 60 * 1000 // 24 hours
const PLAYBACK_RATES = [0.5, 0.75, 1, 1.25, 1.5, 2]

export default {
  name: 'CourseVideoPlayer',
  components: {
    VuePlayer,
  },
  data() {
    return {
      volume: false,
      useNativeControls: true,
      isFullscreen: true,
    }
  },

  props: {
    videoUrl: {
      type: String,
      required: true,
    },
    posterImage: {
      type: String,
      default: '',
    },
    initialPlaybackRate: {
      type: Number,
      default: 1,
    },
    onProgress: {
      type: Function,
      default: () => {},
    },
    onComplete: {
      type: Function,
      default: () => {},
    },
  },

  setup(props) {
    const { notify } = useNotification()
    const playerRef = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const isPlaying = ref(false)
    const isMuted = ref(false)
    const currentTime = ref(0)
    const duration = ref(0)
    const playbackRate = ref(props.initialPlaybackRate)
    const progress = ref(0)
    const savedTime = ref(0)

    // Cache management
    const cacheKey = computed(() => `${VIDEO_CACHE_PREFIX}${props.videoUrl}`)

    const loadVideoProgress = () => {
      try {
        const cached = localStorage.getItem(cacheKey.value)
        if (cached) {
          const data = JSON.parse(cached)
          if (Date.now() - data.timestamp < CACHE_DURATION) {
            savedTime.value = data.currentTime
          } else {
            localStorage.removeItem(cacheKey.value)
          }
        }
      } catch (err) {
        console.error('Failed to load video progress:', err)
      }
    }

    const saveVideoProgress = () => {
      try {
        localStorage.setItem(
          cacheKey.value,
          JSON.stringify({
            currentTime: currentTime.value,
            timestamp: Date.now(),
          }),
        )
      } catch (err) {
        console.error('Failed to save video progress:', err)
      }
    }

    const handleMetadataLoaded = () => {
      console.log('Metadata loaded! Calling onPlayerReady...')
      onPlayerReady()
    }

    // Player event handlers
    const onPlayerReady = () => {
      console.log('here')
      loading.value = false
      error.value = null
      if (playerRef.value) {
        duration.value = playerRef.value.duration
        loadVideoProgress()
      }
    }

    const onTimeUpdate = (time) => {
      currentTime.value = time
      progress.value = (time / duration.value) * 100
      props.onProgress(time)

      // Save progress every 5 seconds
      if (Math.floor(time) % 5 === 0) {
        saveVideoProgress()
      }
    }

    const onVideoEnded = () => {
      isPlaying.value = false
      props.onComplete()
    }

    const onVideoError = (e) => {
      console.error('Video error:', e)
      error.value = 'Failed to load video. Please try again.'
      loading.value = false
      notify.error('Video playback error')
    }

    // Player controls
    const togglePlay = () => {
      if (!playerRef.value) return
      if (isPlaying.value) {
        playerRef.value.pause()
      } else {
        playerRef.value.play()
      }
      isPlaying.value = !isPlaying.value
    }

    const toggleMute = () => {
      if (!playerRef.value) return
      isMuted.value = !isMuted.value
      playerRef.value.muted = isMuted.value
    }

    const onProgressClick = (event) => {
      if (!playerRef.value) return
      const rect = event.target.getBoundingClientRect()
      const pos = (event.clientX - rect.left) / rect.width
      const newTime = pos * duration.value
      playerRef.value.currentTime = newTime
    }

    const setPlaybackRate = (rate) => {
      if (!playerRef.value) return
      playbackRate.value = rate
      playerRef.value.playbackRate = rate
    }

    const togglePlaybackRate = () => {
      const currentIndex = PLAYBACK_RATES.indexOf(playbackRate.value)
      const nextRate = PLAYBACK_RATES[(currentIndex + 1) % PLAYBACK_RATES.length]
      setPlaybackRate(nextRate)
    }

    const toggleFullscreen = async () => {
      if (!playerRef.value) return
      try {
        if (document.fullscreenElement) {
          await document.exitFullscreen()
        } else {
          await playerRef.value.$el.requestFullscreen()
        }
      } catch (err) {
        console.error('Fullscreen error:', err)
        notify.error('Failed to toggle fullscreen')
      }
    }

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const retryLoading = () => {
      loading.value = true
      error.value = null
      if (playerRef.value) {
        playerRef.value.load()
      }
    }

    // Cleanup
    onBeforeUnmount(() => {
      if (playerRef.value) {
        playerRef.value.pause()
      }
      saveVideoProgress()
    })

    return {
      playerRef,
      loading,
      error,
      isPlaying,
      isMuted,
      currentTime,
      duration,
      playbackRate,
      progress,
      savedTime,
      playbackRates: PLAYBACK_RATES,
      onPlayerReady,
      onTimeUpdate,
      onVideoEnded,
      onVideoError,
      togglePlay,
      toggleMute,
      onProgressClick,
      setPlaybackRate,
      togglePlaybackRate,
      toggleFullscreen,
      formatTime,
      retryLoading,
      handleMetadataLoaded,
    }
  },
}
</script>

<style scoped>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}

/* Custom range input styling */
input[type='range'] {
  -webkit-appearance: none;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  background-image: linear-gradient(var(--maroon-500), var(--maroon-500));
  background-repeat: no-repeat;
}

input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 12px;
  width: 12px;
  border-radius: 50%;
  background: var(--maroon-500);
  cursor: pointer;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease-in-out;
}

input[type='range']::-webkit-slider-thumb:hover {
  background: var(--maroon-600);
  transform: scale(1.2);
}

input[type='range']::-webkit-slider-runnable-track {
  -webkit-appearance: none;
  box-shadow: none;
  border: none;
  background: transparent;
}

.aspect-video {
  aspect-ratio: 16 / 9;
}

/* Custom player styles */
:deep(.vue-player) {
  width: 100%;
  height: 100%;
  background-color: black;
}

:deep(.vue-player video) {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Hover states */
.controls-overlay {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.vue-player:hover .controls-overlay {
  opacity: 1;
}

/* Progress bar hover effect */
.progress-bar {
  height: 4px;
  transition: height 0.2s ease;
}

.progress-bar:hover {
  height: 6px;
}

/* Playback rate dropdown */
.playback-rates {
  transform: scale(0.95);
  opacity: 0;
  transition: all 0.2s ease;
}

.playback-rates.show {
  transform: scale(1);
  opacity: 1;
}
</style>
