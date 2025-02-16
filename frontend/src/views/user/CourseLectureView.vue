<template>
  <div class="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <SideNavBar />
    
    <!-- Main Content Container -->
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Loading State -->
      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="w-16 h-16 border-4 border-maroon-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading course content...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto text-red-500">
            <span class="material-icons text-6xl">error_outline</span>
          </div>
          <p class="mt-4 text-gray-800 font-medium">{{ error }}</p>
          <button 
            @click="retryLoading"
            class="mt-4 px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors">
            Retry
          </button>
        </div>
      </div>

      <template v-else>
        <!-- Course Header -->
        <CourseTopNav 
          :course="currentCourse"
          :is-bookmarked="isBookmarked"
          :progress="progress"
          @toggle-bookmark="toggleBookmark"
          @toggle-notes="toggleNotes"
          @back-to-courses="navigateBack"
        />

        <!-- Main Course Layout -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Course Navigation Sidebar -->
          <CourseSideNav 
            :weeks="weeks"
            :selected-lecture="selectedLecture"
            :completed-lectures="completedLectures"
            :total-lectures="totalLectures"
            :is-collapsed="isSidebarCollapsed"
            @select-lecture="selectLecture"
            @toggle-collapse="toggleSidebar"
            class="flex-shrink-0"
          />

          <!-- Main Content Area -->
          <div 
            class="flex-1 overflow-y-auto bg-gradient-to-b from-slate-50 to-white border-l border-slate-200"
            :class="{ 'lg:ml-0': !isSidebarCollapsed }"
          >
            <div class="px-6 py-4 max-w-6xl mx-auto">
              <div v-if="selectedLecture" class="space-y-4">
                <!-- Breadcrumb Navigation -->
                <nav aria-label="Course navigation" class="text-sm mb-3">
                  <ol class="flex items-center space-x-2">
                    <li>
                      <span class="text-slate-500">{{ currentCourse.title }}</span>
                    </li>
                    <li>
                      <span class="text-slate-400 mx-2">›</span>
                      <span class="text-slate-500">Week {{ selectedLecture.week }}</span>
                    </li>
                    <li>
                      <span class="text-slate-400 mx-2">›</span>
                      <span class="text-slate-900">{{ selectedLecture.title }}</span>
                    </li>
                  </ol>
                </nav>

                <!-- Video Player Section -->
                <section aria-label="Lecture video" class="mb-4">
                  <CourseVideoPlayer 
                    :video-url="selectedLecture?.videoUrl || ''"
                    :poster-image="selectedLecture?.thumbnailUrl || ''"
                    :current-time="videoProgress"
                    :use-native-controls="true"
                    @time-update="updateVideoProgress"
                    @video-complete="handleVideoComplete"
                  />
                  
                  <!-- Video Controls -->
                  <div class="flex items-center justify-between mt-2">
                    <div class="flex items-center space-x-4">
                      <button
                        @click="togglePlaybackSpeed"
                        class="px-3 py-1 text-sm bg-slate-100 rounded-full hover:bg-slate-200 transition-colors flex items-center space-x-1"
                      >
                        <span class="material-symbols-outlined text-sm">speed</span>
                        <span>{{ playbackSpeed }}x</span>
                      </button>
                      <button
                        @click="toggleCaptions"
                        class="px-3 py-1 text-sm bg-slate-100 rounded-full hover:bg-slate-200 transition-colors flex items-center space-x-1"
                        :class="{ 'bg-maroon-100 text-maroon-600': captionsEnabled }"
                      >
                        <span class="material-symbols-outlined text-sm">closed_caption</span>
                        <span>CC</span>
                      </button>
                    </div>
                    <div class="flex items-center space-x-2">
                      <button
                        @click="toggleFullscreen"
                        class="p-2 rounded-full hover:bg-slate-100 transition-colors"
                      >
                        <span class="material-symbols-outlined">fullscreen</span>
                      </button>
                    </div>
                  </div>
                </section>

                <!-- Lecture Content -->
                <div class="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-4">
                  <div class="xl:col-span-2 space-y-8">
                    <!-- Lecture Info -->
                    <div class="bg-white rounded-2xl shadow-lg p-6">
                      <div class="flex items-start justify-between">
                        <div class="space-y-3">
                          <h2 class="text-2xl font-bold text-slate-900">{{ selectedLecture.title }}</h2>
                          <p class="text-slate-600 leading-relaxed">{{ selectedLecture.description }}</p>
                        </div>
                        <div class="relative w-20 h-20">
                          <svg class="progress-ring" width="80" height="80">
                            <circle class="text-slate-200" stroke-width="6" fill="transparent" r="37" cx="40" cy="40"></circle>
                            <circle class="text-maroon-500" stroke-width="6" stroke-dasharray="NaN, 234" fill="transparent" r="37" cx="40" cy="40" 
                                    style="filter: drop-shadow(0 0 8px rgba(139, 0, 0, 0.2));"></circle>
                          </svg>
                          <button class="absolute inset-0 flex items-center justify-center w-full h-full transition-transform duration-300 hover:scale-105">
                            <span class="material-symbols-outlined text-3xl" 
                                  :class="isLectureCompleted ? 'text-emerald-500' : 'text-maroon-500'">
                              {{ isLectureCompleted ? 'check_circle' : 'play_circle' }}
                            </span>
                          </button>
                        </div>
                      </div>
                      <div class="mt-6 flex flex-wrap gap-3">
                        <button class="px-5 py-2.5 bg-maroon-500 text-white rounded-xl hover:bg-maroon-600 
                                     transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg">
                          <span class="material-symbols-outlined">download</span>
                          <span>Resources</span>
                        </button>
                      </div>
                    </div>

                    <!-- Key Concepts -->
                    <div class="bg-white rounded-2xl shadow-lg p-6">
                      <h3 class="text-xl font-bold text-slate-900 mb-5">Key Concepts</h3>
                      <ul class="space-y-4">
                        <li v-for="(concept, index) in selectedLecture.concepts" 
                            :key="index"
                            class="flex items-start space-x-3 p-3 bg-slate-50/50 rounded-lg hover:bg-slate-50 transition-colors">
                          <span class="material-symbols-outlined text-emerald-500 mt-1">check_circle</span>
                          <span class="text-slate-700 leading-relaxed">{{ concept }}</span>
                        </li>
                      </ul>
                    </div>

                    <!-- Discussion -->
                    <div class="bg-white rounded-2xl shadow-lg p-6">
                      <h3 class="text-xl font-bold text-slate-900 mb-5">Community Dialogue</h3>
                      <div class="space-y-5">
                        <textarea
                          placeholder="Engage with peers..."
                          class="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-maroon-500 focus:border-transparent transition-all duration-300 resize-none"
                          rows="3"
                        ></textarea>
                        <div class="flex items-center justify-between">
                          <div class="flex items-center space-x-2 text-slate-500">
                            <button class="p-2 hover:bg-slate-100 rounded-lg">
                              <span class="material-symbols-outlined">attach_file</span>
                            </button>
                            <button class="p-2 hover:bg-slate-100 rounded-lg">
                              <span class="material-symbols-outlined">alternate_email</span>
                            </button>
                          </div>
                          <button class="px-6 py-2.5 bg-maroon-500 text-white rounded-xl hover:bg-maroon-600 
                                       transition-all duration-300 flex items-center space-x-2 shadow-md">
                            <span class="material-symbols-outlined">send</span>
                            <span>Post</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Sidebar Content -->
                  <div class="space-y-8">
                    <!-- Resources -->
                    <div class="bg-white rounded-2xl shadow-lg p-6">
                      <h3 class="text-xl font-bold text-slate-900 mb-5">Learning Toolkit</h3>
                      <ul class="space-y-3">
                        <li v-for="(resource, index) in selectedLecture.resources" 
                            :key="index"
                            class="flex items-center justify-between p-3 bg-slate-50/50 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer group">
                          <div class="flex items-center space-x-3">
                            <span class="material-symbols-outlined text-lg transform transition-all group-hover:scale-110"
                                  :class="getResourceIcon(resource.type).color">
                              {{ getResourceIcon(resource.type).icon }}
                            </span>
                            <span class="text-sm font-medium text-slate-700">{{ resource.title }}</span>
                          </div>
                          <button class="p-2 hover:bg-slate-200 rounded-lg transition-colors">
                            <span class="material-symbols-outlined text-maroon-500">download</span>
                          </button>
                        </li>
                      </ul>
                    </div>

                    <!-- Challenges -->
                    <div class="bg-white rounded-2xl shadow-lg p-6">
                      <h3 class="text-xl font-bold text-slate-900 mb-5">Skill Challenges</h3>
                      <ul class="space-y-4">
                        <li v-for="(challenge, index) in selectedLecture.challenges" 
                            :key="index"
                            class="p-3 bg-slate-50/50 rounded-lg hover:bg-slate-50 transition-colors">
                          <div class="flex items-start space-x-3">
                            <span class="flex-shrink-0 w-7 h-7 bg-maroon-100 text-maroon-600 rounded-lg flex items-center justify-center text-sm font-bold">
                              {{ index + 1 }}
                            </span>
                            <p class="text-slate-700 leading-relaxed">{{ challenge.question }}</p>
                          </div>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- Navigation Buttons -->
                <div class="flex items-center justify-between pt-4 border-t border-slate-200">
                  <button
                    v-if="previousLecture"
                    @click="selectLecture(previousLecture)"
                    class="flex items-center space-x-2 text-slate-600 hover:text-maroon-600 transition-colors"
                  >
                    <span class="material-symbols-outlined">arrow_back</span>
                    <span>Previous Lecture</span>
                  </button>
                  <div class="flex-1"></div>
                  <button
                    v-if="nextLecture"
                    @click="selectLecture(nextLecture)"
                    class="flex items-center space-x-2 text-slate-600 hover:text-maroon-600 transition-colors"
                  >
                    <span>Next Lecture</span>
                    <span class="material-symbols-outlined">arrow_forward</span>
                  </button>
                </div>
              </div>

              <!-- Empty State -->
              <div v-else class="h-full flex items-center justify-center">
                <div class="text-center max-w-md py-12 space-y-6">
                  <div class="inline-flex p-6 bg-maroon-50 rounded-2xl">
                    <span class="material-symbols-outlined text-4xl text-maroon-600">school</span>
                  </div>
                  <h2 class="text-2xl font-bold text-slate-900">Begin Your Learning Journey</h2>
                  <p class="text-slate-600">Select a module from the curriculum to start learning</p>
                  <button
                    @click="selectFirstLecture"
                    class="px-6 py-3 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
                  >
                    Start First Lecture
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes Panel -->
          <div 
            v-if="showNotes"
            class="w-96 border-l border-gray-200 bg-white overflow-hidden flex flex-col transition-all duration-300"
          >
            <div class="p-4 border-b border-gray-200 flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-900">Lecture Notes</h2>
              <button 
                @click="toggleNotes"
                class="p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <span class="material-icons">close</span>
              </button>
            </div>
            <div class="flex-1 overflow-y-auto p-4">
              <textarea
                v-model="currentNotes"
                placeholder="Take notes for this lecture..."
                class="w-full h-full p-4 border rounded-lg resize-none focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
                @input="autoSaveNotes"
              ></textarea>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SideNavBar from '@/layouts/SideNavBar.vue'
import CourseTopNav from '@/components/course/CourseTopNav.vue'
import CourseSideNav from '@/components/course/CourseSideNav.vue'
import CourseVideoPlayer from '@/components/course/CourseVideoPlayer.vue'
import CourseLectureContent from '@/components/course/CourseLectureContent.vue'
import { useCourse } from '@/composables/useCourse'
import { useNotification } from '@/composables/useNotification'

export default {
  name: 'CourseLectureView',
  components: { 
    SideNavBar,
    CourseTopNav,
    CourseSideNav,
    CourseVideoPlayer,
    CourseLectureContent
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const { notify } = useNotification()
    
    // State
    const loading = ref(true)
    const error = ref(null)
    const isSidebarCollapsed = ref(false)
    const playbackSpeed = ref(1)
    const captionsEnabled = ref(false)
    const videoProgress = ref(0)
    const autoSaveTimeout = ref(null)
    
    // Course Data & Methods
    const courseId = route.params.courseId
    const {
      currentCourse,
      selectedLecture,
      isBookmarked,
      showNotes,
      currentNotes,
      completedLectures,
      totalLectures,
      weeks,
      selectLecture,
      toggleBookmark,
      toggleNotes,
      markAsComplete,
      getWeekProgress,
      getFileIcon,
      saveNotes,
      completedLecturesCount
    } = useCourse(courseId)

    // Computed Properties
    const progress = computed(() => {
      if (!currentCourse.value) return 0
      return Math.round((completedLecturesCount.value / totalLectures.value) * 100)
    })

    const previousLecture = computed(() => {
      if (!selectedLecture.value || !weeks.value) return null
      
      let prevLecture = null
      let foundCurrent = false
      
      // Iterate through weeks in reverse to find previous lecture
      for (let weekIndex = weeks.value.length - 1; weekIndex >= 0; weekIndex--) {
        const week = weeks.value[weekIndex]
        for (let lectureIndex = week.lectures.length - 1; lectureIndex >= 0; lectureIndex--) {
          const lecture = week.lectures[lectureIndex]
          if (foundCurrent) {
            prevLecture = lecture
            break
          }
          if (lecture.id === selectedLecture.value.id) {
            foundCurrent = true
          }
        }
        if (prevLecture) break
      }
      
      return prevLecture
    })

    const nextLecture = computed(() => {
      if (!selectedLecture.value || !weeks.value) return null
      
      let nextLecture = null
      let foundCurrent = false
      
      // Iterate through weeks to find next lecture
      for (const week of weeks.value) {
        for (const lecture of week.lectures) {
          if (foundCurrent) {
            nextLecture = lecture
            break
          }
          if (lecture.id === selectedLecture.value.id) {
            foundCurrent = true
          }
        }
        if (nextLecture) break
      }
      
      return nextLecture
    })

    const isLectureCompleted = computed(() => {
      return completedLectures.value.includes(selectedLecture.value?.id)
    })

    // Methods
    const loadCourseData = async () => {
      try {
        loading.value = true
        // API call to load course data
        loading.value = false
      } catch (err) {
        error.value = 'Failed to load course content. Please try again.'
        loading.value = false
      }
    }

    const retryLoading = () => {
      error.value = null
      loadCourseData()
    }

    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
    }

    const togglePlaybackSpeed = () => {
      const speeds = [0.5, 1, 1.25, 1.5, 2]
      const currentIndex = speeds.indexOf(playbackSpeed.value)
      playbackSpeed.value = speeds[(currentIndex + 1) % speeds.length]
    }

    const toggleCaptions = () => {
      captionsEnabled.value = !captionsEnabled.value
    }

    const updateVideoProgress = (time) => {
      videoProgress.value = time
      // Save progress to backend
    }

    const handleVideoComplete = () => {
      if (!isLectureCompleted.value) {
        markAsComplete(selectedLecture.value.id)
      }
    }

    const autoSaveNotes = () => {
      if (autoSaveTimeout.value) {
        clearTimeout(autoSaveTimeout.value)
      }
      autoSaveTimeout.value = setTimeout(() => {
        saveNotes(selectedLecture.value.id, currentNotes.value)
      }, 1000)
    }

    const handleResourceDownload = async (resource) => {
      try {
        // API call to download resource
        notify.success('Download started')
      } catch (err) {
        notify.error('Failed to download resource')
      }
    }

    const navigateBack = () => {
      router.push('/user/courses')
    }

    const getResourceIcon = (type) => {
      const icons = {
        pdf: {
          icon: 'description',
          color: 'text-maroon-500'
        },
        doc: {
          icon: 'article',
          color: 'text-maroon-400'
        },
        ppt: {
          icon: 'slideshow',
          color: 'text-yellow-500'
        },
        code: {
          icon: 'code',
          color: 'text-yellow-600'
        },
        zip: {
          icon: 'folder_zip',
          color: 'text-yellow-400'
        },
        video: {
          icon: 'play_circle',
          color: 'text-maroon-600'
        }
      };
      return icons[type] || { icon: 'insert_drive_file', color: 'text-slate-500' };
    }

    // Lifecycle Hooks
    onMounted(() => {
      loadCourseData()
      // Restore video progress from saved state
    })

    onBeforeUnmount(() => {
      if (autoSaveTimeout.value) {
        clearTimeout(autoSaveTimeout.value)
      }
      // Save final state
    })

    // Watch for route changes to update content
    watch(
      () => route.params.courseId,
      (newId) => {
        if (newId && newId !== courseId) {
          loadCourseData()
        }
      }
    )

    return {
      // State
      loading,
      error,
      isSidebarCollapsed,
      playbackSpeed,
      captionsEnabled,
      videoProgress,
      
      // Course Data
      currentCourse,
      selectedLecture,
      isBookmarked,
      showNotes,
      currentNotes,
      completedLectures,
      totalLectures,
      weeks,
      progress,
      previousLecture,
      nextLecture,
      isLectureCompleted,
      
      // Methods
      selectLecture,
      toggleBookmark,
      toggleNotes,
      toggleSidebar,
      togglePlaybackSpeed,
      toggleCaptions,
      updateVideoProgress,
      handleVideoComplete,
      autoSaveNotes,
      handleResourceDownload,
      retryLoading,
      navigateBack,
      getFileIcon,
      markAsComplete,
      getResourceIcon
    }
  }
}
</script>

<style>
:root {
  /* Primary Colors - Maroon (Adjusted to be less bright) */
  --maroon-50: #fdf2f2;
  --maroon-100: #f3e2e2;
  --maroon-200: #dbc1c1;
  --maroon-300: #c39e9e;
  --maroon-400: #a67979;
  --maroon-500: #8b4444;
  --maroon-600: #722b2b;
  --maroon-700: #591f1f;
  --maroon-800: #411616;
  --maroon-900: #2c0f0f;

  /* Secondary Colors - Yellow (Muted to match maroon) */
  --yellow-50: #fdfaeb;
  --yellow-100: #fdf2c7;
  --yellow-200: #f8e3a3;
  --yellow-300: #f6d47e;
  --yellow-400: #e9b64d;
  --yellow-500: #d49b35;
  --yellow-600: #b37d24;
  --yellow-700: #8c5e1a;
  --yellow-800: #674415;
  --yellow-900: #4d3110;

  /* Neutral Colors - Slate (Kept as is for contrast) */
  --slate-50: #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1e293b;
  --slate-900: #0f172a;
}

/* Progress Ring Styles */
.progress-ring circle {
  transition: stroke-dasharray 0.5s ease-out;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
}

.progress-ring circle.text-slate-200 {
  stroke: var(--slate-200);
}

.progress-ring circle.text-maroon-500 {
  stroke: var(--maroon-500);
  filter: drop-shadow(0 0 4px rgba(114, 43, 43, 0.2));
}

/* Button Styles */
.btn-primary {
  @apply bg-maroon-600 text-white hover:bg-maroon-700 active:bg-maroon-800 
         shadow-sm hover:shadow-md transition-all duration-200;
}

.btn-secondary {
  @apply bg-slate-100 text-slate-700 hover:bg-slate-200 active:bg-slate-300
         shadow-sm transition-all duration-200;
}

/* Card Styles */
.card {
  @apply bg-white rounded-2xl shadow-sm hover:shadow-md transition-all duration-200
         border border-slate-200/80;
}

/* Icon Colors */
.icon-primary {
  @apply text-maroon-600;
}

.icon-secondary {
  @apply text-yellow-600;
}

.icon-neutral {
  @apply text-slate-400;
}

/* Hover Effects */
.hover-primary {
  @apply hover:text-maroon-600 hover:bg-maroon-50;
}

.hover-secondary {
  @apply hover:text-yellow-600 hover:bg-yellow-50;
}

/* Focus States */
.focus-primary {
  @apply focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2;
}

/* Button States */
.btn-maroon {
  @apply bg-maroon-600 text-white hover:bg-maroon-700 
         shadow-sm hover:shadow-md transition-all duration-200;
}

.btn-maroon-light {
  @apply bg-maroon-50 text-maroon-600 hover:bg-maroon-100 
         shadow-sm transition-all duration-200;
}

/* Progress Bars */
.progress-bar-bg {
  @apply bg-slate-100;
}

.progress-bar-fill {
  @apply bg-gradient-to-r from-maroon-600 to-maroon-500;
}

/* Status Indicators */
.status-complete {
  @apply text-emerald-600;
}

.status-incomplete {
  @apply text-maroon-500;
}

/* Interactive Elements */
.interactive-element {
  @apply transition-all duration-200 ease-in-out;
}

.interactive-hover {
  @apply transform hover:scale-105 transition-transform duration-200;
}

.interactive-press {
  @apply transform active:scale-95 transition-transform duration-100;
}

/* Card and Button Base Styles */
.card-base {
  @apply bg-white rounded-2xl shadow-sm hover:shadow-md 
         border border-slate-200 transition-all duration-200;
}

.button-base {
  @apply rounded-lg transition-all duration-200 
         focus:outline-none focus:ring-2 focus:ring-offset-2;
}

/* Custom Backgrounds */
.bg-gradient-maroon {
  @apply bg-gradient-to-r from-maroon-600 to-maroon-500;
}

.bg-gradient-yellow {
  @apply bg-gradient-to-r from-yellow-600 to-yellow-500;
}

/* Custom Shadows */
.shadow-maroon {
  box-shadow: 0 4px 14px -2px rgba(114, 43, 43, 0.12);
}

.shadow-hover {
  @apply transition-shadow duration-200 hover:shadow-lg;
}

/* Status Colors */
.status-success {
  @apply text-emerald-600 bg-emerald-50;
}

.status-pending {
  @apply text-maroon-600 bg-maroon-50;
}

.status-neutral {
  @apply text-slate-600 bg-slate-50;
}

/* Icon Styles */
.icon-container {
  @apply flex items-center justify-center w-10 h-10 rounded-lg 
         transition-all duration-200;
}

.icon-primary {
  @apply text-maroon-600 bg-maroon-50 hover:bg-maroon-100;
}

.icon-secondary {
  @apply text-yellow-600 bg-yellow-50 hover:bg-yellow-100;
}

.icon-neutral {
  @apply text-slate-600 bg-slate-50 hover:bg-slate-100;
}

/* Material Icons Styles */
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}

.material-symbols-outlined.filled {
  font-variation-settings:
    'FILL' 1,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}

/* Custom Gradients */
.gradient-primary {
  @apply bg-gradient-to-r from-maroon-600 to-maroon-500;
}

.gradient-secondary {
  @apply bg-gradient-to-r from-yellow-600 to-yellow-500;
}

/* Transitions */
.transition-smooth {
  @apply transition-all duration-300 ease-in-out;
}
</style>