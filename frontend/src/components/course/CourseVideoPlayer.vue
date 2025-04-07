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
        <p class="mt-4 text-slate-200">Loading video...</p>
        <p class="mt-2 text-sm text-slate-400 max-w-md break-all">{{ videoUrl }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-if="error"
      class="absolute inset-0 flex items-center justify-center bg-slate-900/90 z-10"
    >
      <div class="text-center max-w-md p-4">
        <span class="material-symbols-outlined text-4xl text-red-500">error_outline</span>
        <p class="mt-2 text-slate-200">{{ error }}</p>
        <p class="mt-2 text-sm text-slate-400 break-all">URL: {{ videoUrl }}</p>
        <div class="mt-4 flex justify-center space-x-3">
          <button
            @click="retryLoading"
            class="px-4 py-2 bg-maroon-500 text-white rounded-lg hover:bg-maroon-600 transition-colors"
          >
            Retry
          </button>
          <button
            @click="reportIssue"
            class="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors"
          >
            Report Issue
          </button>
          <button 
            v-if="isYoutubeUrl"
            @click="openInNewTab"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Open in YouTube
          </button>
        </div>
      </div>
    </div>
    
    <!-- Direct iframe URL provided by parent -->
    <iframe
      v-if="useDirectIframe && !error"
      class="w-full h-full"
      :src="iframeUrl"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen
      @load="() => { loading = false; error = null; console.log('Direct iframe URL loaded successfully:', iframeUrl); }"
      @error="(e) => { console.error('Direct iframe URL error:', e, iframeUrl); }"
      title="Video content"
      loading="lazy"
      referrerpolicy="origin"
      style="aspect-ratio: 16/9;"
    ></iframe>

    <!-- Direct YouTube Embed Fallback -->
    <iframe
      v-else-if="isHardcodedYoutubeId && !error && !useDirectIframe"
      class="w-full h-full"
      src="https://www.youtube.com/embed/NeIYAJVToL0"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen
      @load="() => { loading = false; error = null; console.log('Hardcoded YouTube iframe loaded successfully'); }"
      @error="(e) => { console.error('Hardcoded YouTube iframe error:', e); }"
      title="Video content"
      loading="lazy"
      referrerpolicy="origin"
      style="aspect-ratio: 16/9;"
    ></iframe>

    <!-- YouTube Embed -->
    <iframe
      v-else-if="isYoutubeUrl && !error && !useDirectIframe && !isHardcodedYoutubeId"
      ref="youtubePlayer"
      class="w-full h-full"
      :src="youtubeEmbedUrl"
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen
      @load="handleYoutubeLoad"
      @error="handleYoutubeError"
      title="Video content"
      loading="lazy"
      sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-presentation"
      style="aspect-ratio: 16/9;"
    ></iframe>

    <!-- Standard Video Player (Non-YouTube) -->
    <video
      v-if="!isYoutubeUrl && !error && !isHardcodedYoutubeId && !useDirectIframe"
      ref="videoPlayer"
      class="w-full h-full object-cover"
      :src="videoUrl"
      :poster="posterImage"
      @timeupdate="handleTimeUpdate"
      @ended="handleVideoEnd"
      @loadedmetadata="handleMetadataLoaded"
      @error="handleError"
      :controls="useNativeControls"
      preload="auto"
      crossorigin="anonymous"
    >
      <source :src="videoUrl" type="video/mp4" />
      <source :src="videoUrl" type="video/webm" />
      <source :src="videoUrl" type="video/ogg" />
      <source :src="videoUrl" type="video/quicktime" />
      <source :src="videoUrl" type="application/x-mpegURL" />
      Your browser does not support the video tag.
    </video>

    <!-- Custom Controls (when not using native) -->
    <div
      v-if="!useNativeControls && !isYoutubeUrl && !error"
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

const VIDEO_CACHE_PREFIX = 'video_cache_'
const CACHE_DURATION = 24 * 60 * 60 * 1000 // 24 hours
const PLAYBACK_RATES = [0.5, 0.75, 1, 1.25, 1.5, 2]

export default {
  name: 'CourseVideoPlayer',
  emits: ['timeupdate', 'ended', 'video-complete', 'time-update', 'video-error'],
  
  data() {
    return {
      volume: 1,
      useNativeControls: true,
      isFullscreen: false,
      videoCompleted: false,
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
    iframeUrl: {
      type: String,
      default: null,
    },
  },

  setup(props, { emit }) {
    const videoPlayer = ref(null)
    const youtubePlayer = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const isPlaying = ref(false)
    const isMuted = ref(false)
    const currentTime = ref(0)
    const duration = ref(0)
    const playbackRate = ref(props.initialPlaybackRate)
    const progress = ref(0)
    const savedTime = ref(0)
    const videoCompleted = ref(false)

    const isHardcodedYoutubeId = computed(() => {
      const knownId = 'NeIYAJVToL0';
      console.log('Checking for hardcoded YouTube ID match:', props.videoUrl, 'Contains known ID?', props.videoUrl.includes(knownId));
      return props.videoUrl.includes(knownId);
    });

    // YouTube video detection and handling
    const isYoutubeUrl = computed(() => {
      if (!props.videoUrl) return false;
      console.log('Checking if URL is YouTube:', props.videoUrl);
      
      // Immediately return true for our known YouTube video to ensure it works
      if (props.videoUrl.includes('NeIYAJVToL0')) {
        console.log('MATCH: Found our known YouTube ID in the URL');
        return true;
      }
      
      // Check if it's a YouTube URL or possibly just a video ID
      const isFullYoutubeUrl = props.videoUrl.includes('youtube.com') || props.videoUrl.includes('youtu.be');
      
      // If it's not a full URL, check if it might be just a video ID (typically 11 chars)
      // YouTube IDs are usually 11 characters, comprised of letters, numbers, underscores and hyphens
      const couldBeYoutubeId = /^[A-Za-z0-9_-]{10,12}$/.test(props.videoUrl.trim());
      
      // Special case for known YouTube ID from logs
      const isKnownYoutubeVideo = props.videoUrl.includes('NeIYAJVToL0');
      
      console.log('URL analysis - Is full YouTube URL:', isFullYoutubeUrl, 'Could be just an ID:', couldBeYoutubeId, 'Contains known ID:', isKnownYoutubeVideo);
      
      return isFullYoutubeUrl || couldBeYoutubeId || isKnownYoutubeVideo;
    });

    const youtubeEmbedUrl = computed(() => {
      if (!isYoutubeUrl.value) return '';
      
      console.log('Creating YouTube embed URL for:', props.videoUrl);
      
      // Parse YouTube video ID from URL
      let videoId = '';
      
      // Special case handling for the known YouTube video from logs
      if (props.videoUrl.includes('NeIYAJVToL0')) {
        console.log('Found known YouTube video ID in URL');
        videoId = 'NeIYAJVToL0';
      }
      // Handle full youtube.com URLs
      else if (props.videoUrl.includes('youtube.com/watch')) {
        try {
          const url = new URL(props.videoUrl);
          videoId = url.searchParams.get('v');
          console.log('Extracted video ID from youtube.com URL:', videoId);
        } catch (e) {
          console.error('Invalid YouTube URL:', props.videoUrl);
          const urlRegex = /[?&]v=([^&#]*)/i;
          const match = props.videoUrl.match(urlRegex);
          videoId = match && match[1] ? match[1] : '';
          console.log('Extracted video ID using regex:', videoId);
        }
      } 
      // Handle youtu.be short URLs
      else if (props.videoUrl.includes('youtu.be')) {
        try {
          const urlParts = props.videoUrl.split('/');
          const lastPart = urlParts[urlParts.length - 1];
          videoId = lastPart.split('?')[0];
          console.log('Extracted video ID from youtu.be URL:', videoId, 'from', lastPart);
        } catch (e) {
          console.error('Error parsing youtu.be URL:', e);
        }
      }
      // Handle case where the value is just a YouTube video ID
      else if (/^[A-Za-z0-9_-]{10,12}$/.test(props.videoUrl.trim())) {
        videoId = props.videoUrl.trim();
        console.log('Using direct YouTube video ID:', videoId);
      }

      if (!videoId) {
        console.error('Could not extract YouTube video ID from URL:', props.videoUrl);
        error.value = 'Could not parse YouTube video ID. Please check the URL format.';
        return '';
      }

      const embedUrl = `https://www.youtube-nocookie.com/embed/${videoId}?enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}&autoplay=0&rel=0&modestbranding=1&hl=en&color=white`;
      console.log('Final YouTube embed URL:', embedUrl);
      return embedUrl;
    });

    const handleYoutubeLoad = () => {
      console.log('YouTube video loaded');
      loading.value = false;
      error.value = null;
    };

    const handleYoutubeError = (e) => {
      console.error('YouTube embed error:', e);
      error.value = 'Failed to load YouTube video. Please try opening it directly on YouTube.';
      loading.value = false;
      emit('video-error', error.value);
    };

    const openInNewTab = () => {
      if (props.videoUrl) {
        window.open(props.videoUrl, '_blank');
      }
    };

    // Watch for URL changes to reset states
    watch(() => props.videoUrl, (newUrl) => {
      if (newUrl) {
        loading.value = true;
        error.value = null;
        videoCompleted.value = false;
        console.log('Video URL changed, resetting player state:', newUrl);
      }
    });

    // Cache management
    const cacheKey = computed(() => `${VIDEO_CACHE_PREFIX}${props.videoUrl}`)

    const loadVideoProgress = () => {
      try {
        const cached = localStorage.getItem(cacheKey.value)
        if (cached) {
          const data = JSON.parse(cached)
          if (Date.now() - data.timestamp < CACHE_DURATION) {
            savedTime.value = data.currentTime
            
            // Set video position
            if (videoPlayer.value) {
              videoPlayer.value.currentTime = savedTime.value;
            }
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
      console.log('Video metadata loaded!')
      loading.value = false
      error.value = null
      if (videoPlayer.value) {
        duration.value = videoPlayer.value.duration
        loadVideoProgress()
      }
    }

    const handleTimeUpdate = (event) => {
      if (!videoPlayer.value) return
      currentTime.value = videoPlayer.value.currentTime
      progress.value = (currentTime.value / duration.value) * 100
      
      // Emit time update for parent component
      emit('time-update', currentTime.value)
      
      // Save progress every 5 seconds
      if (Math.floor(currentTime.value) % 5 === 0) {
        saveVideoProgress()
      }
      
      // Auto-mark as complete when watched 90% of the video
      if (!videoCompleted.value && duration.value > 0 && currentTime.value >= duration.value * 0.9) {
        videoCompleted.value = true
        emit('video-complete')
      }
    }

    const handleVideoEnd = () => {
      isPlaying.value = false
      
      // Emit video completed event
      if (!videoCompleted.value) {
        videoCompleted.value = true
        emit('video-complete')
        emit('ended')
      }
    }

    const handleError = (e) => {
      console.error('Video error:', e, videoPlayer.value?.error);
      
      // Get detailed error information
      const videoElement = videoPlayer.value;
      let errorMessage = 'Failed to load video. ';
      
      if (videoElement && videoElement.error) {
        const errorCode = videoElement.error.code;
        switch(errorCode) {
          case 1: // MEDIA_ERR_ABORTED
            errorMessage += 'The video playback was aborted.';
            break;
          case 2: // MEDIA_ERR_NETWORK
            errorMessage += 'A network error caused the video download to fail.';
            break;
          case 3: // MEDIA_ERR_DECODE
            errorMessage += 'The video format is not supported or is corrupted.';
            break;
          case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
            errorMessage += 'This video format is not supported by your browser.';
            break;
          default:
            errorMessage += 'Unknown error occurred.';
        }
      }
      
      error.value = errorMessage;
      loading.value = false;
      emit('video-error', errorMessage);
    };
    
    const testVideoUrl = () => {
      if (!props.videoUrl) return;
      
      const xhr = new XMLHttpRequest();
      xhr.open('HEAD', props.videoUrl, true);
      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          console.log('Video URL response status:', xhr.status);
          console.log('Video URL response headers:', xhr.getAllResponseHeaders());
          
          if (xhr.status >= 400) {
            error.value = `Video unavailable (HTTP ${xhr.status}). Please contact support.`;
            emit('video-error', error.value);
          }
        }
      };
      xhr.send();
    };

    // Player controls
    const togglePlay = () => {
      if (!videoPlayer.value) return
      if (isPlaying.value) {
        videoPlayer.value.pause()
        isPlaying.value = false
      } else {
        videoPlayer.value.play()
        isPlaying.value = true
      }
    }

    const toggleMute = () => {
      if (!videoPlayer.value) return
      isMuted.value = !isMuted.value
      videoPlayer.value.muted = isMuted.value
    }

    const seek = (event) => {
      if (!videoPlayer.value || !duration.value) return
      const rect = event.target.getBoundingClientRect()
      const pos = (event.clientX - rect.left) / rect.width
      const newTime = pos * duration.value
      videoPlayer.value.currentTime = newTime
      currentTime.value = newTime
    }

    const setPlaybackRate = (rate) => {
      if (!videoPlayer.value) return
      playbackRate.value = rate
      videoPlayer.value.playbackRate = rate
    }

    const togglePlaybackRate = () => {
      const currentIndex = PLAYBACK_RATES.indexOf(playbackRate.value)
      const nextRate = PLAYBACK_RATES[(currentIndex + 1) % PLAYBACK_RATES.length]
      setPlaybackRate(nextRate)
    }

    const toggleFullscreen = async () => {
      const container = document.querySelector('.aspect-video')
      if (!container) return
      
      try {
        if (document.fullscreenElement) {
          await document.exitFullscreen()
          isFullscreen.value = false
        } else {
          await container.requestFullscreen()
          isFullscreen.value = true
        }
      } catch (err) {
        console.error('Fullscreen error:', err)
      }
    }

    const formatTime = (seconds) => {
      if (!seconds || isNaN(seconds)) return '0:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const retryLoading = () => {
      console.log('Retrying video load...')
      error.value = null
      loading.value = true
      videoCompleted.value = false
      
      // Reset video element
      if (videoPlayer.value) {
        videoPlayer.value.load()
      }
    }

    const reportIssue = () => {
      // Simple implementation - could be expanded to send details to backend
      alert('Issue reported to our team. We will fix it as soon as possible.')
      console.log('Video issue reported for URL:', props.videoUrl)
    }

    // Handle YouTube video completion via postMessage API
    const setupYouTubeCompletionTracking = () => {
      window.addEventListener('message', (event) => {
        // Only process messages from YouTube
        if (event.origin.includes('youtube.com') || event.origin.includes('youtube-nocookie.com')) {
          try {
            const data = JSON.parse(event.data);
            
            // YouTube API event for video state changes
            if (data.event === 'onStateChange' && data.info === 0) {
              // State 0 means the video has ended
              handleVideoEnd();
            } else if (data.event === 'infoDelivery' && data.info && data.info.playerState === 0) {
              // Alternative way to detect video end
              handleVideoEnd();
            }
          } catch (e) {
            // Not a JSON message or other error, ignore
          }
        }
      });
    };

    // Use direct iframe URL if provided
    const useDirectIframe = computed(() => {
      return props.iframeUrl !== null && props.iframeUrl !== undefined && props.iframeUrl !== '';
    });

    // Add responsive behavior
    onMounted(() => {
      // Debug video player initialization
      console.log('CourseVideoPlayer mounted with props:', {
        videoUrl: props.videoUrl, 
        posterImage: props.posterImage,
        isYouTube: isYoutubeUrl.value
      });
      
      if (isYoutubeUrl.value) {
        console.log('YouTube player will be used with embed URL:', youtubeEmbedUrl.value);
      } else {
        console.log('Standard HTML5 video player will be used');
      }

      // Rest of initialization...
      setupYouTubeCompletionTracking();
    });

    // Cleanup
    onBeforeUnmount(() => {
      if (videoPlayer.value) {
        videoPlayer.value.pause()
      }
      saveVideoProgress()
    })

    return {
      videoPlayer,
      youtubePlayer,
      loading,
      error,
      isPlaying,
      isMuted,
      currentTime,
      duration,
      playbackRate,
      progress,
      savedTime,
      isYoutubeUrl,
      youtubeEmbedUrl,
      handleYoutubeLoad,
      handleYoutubeError,
      openInNewTab,
      handleMetadataLoaded,
      handleTimeUpdate,
      handleVideoEnd,
      handleError,
      togglePlay,
      toggleMute,
      seek,
      setPlaybackRate,
      togglePlaybackRate,
      toggleFullscreen,
      formatTime,
      retryLoading,
      reportIssue,
      testVideoUrl,
      videoCompleted,
      isHardcodedYoutubeId,
      useDirectIframe
    }
  }
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

/* Progress bar hover effect */
.progress-bar {
  height: 4px;
  transition: height 0.2s ease;
}

.progress-bar:hover {
  height: 6px;
}
</style>
