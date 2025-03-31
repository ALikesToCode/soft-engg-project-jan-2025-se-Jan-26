<template>
  <div class="min-h-screen flex flex-col md:flex-row">
    <!-- Course Sidebar Navigation -->
    <CourseSideNav 
      v-if="course" 
      :weeks="courseWeeks"
      :selectedLecture="currentLecture" 
      :completedLectures="completedLectures"
      :totalLectures="totalLectureCount"
      :isCollapsed="!sidebarOpen"
      @toggle="toggleSidebar"
      @select-lecture="handleLectureSelection"
    />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col w-full max-h-screen overflow-hidden">
      <!-- Top Navigation -->
      <div v-if="course && currentLecture" class="sticky top-0 z-10 bg-white border-b border-gray-200 dark:border-gray-700 dark:bg-gray-800 shadow-sm">
        <div class="px-4 py-3 md:px-6 md:py-4 flex items-center justify-between">
          <!-- Left Side -->
          <div class="flex items-center">
            <button
              @click="toggleSidebar"
              class="p-2 mr-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
              :aria-label="sidebarOpen ? 'Hide course navigation' : 'Show course navigation'"
            >
              <span class="material-symbols-outlined">{{ sidebarOpen ? 'menu_open' : 'menu' }}</span>
            </button>
            <div>
              <h1 class="text-lg font-semibold text-gray-900 dark:text-white md:text-xl truncate max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg">
                {{ currentLecture.title }}
              </h1>
              <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <span>{{ course.title }}</span>
                <span class="mx-2">•</span>
                <span>{{ getCurrentWeekName() }}</span>
              </div>
            </div>
          </div>
          
          <!-- Right Side - Lecture Navigation -->
          <div class="flex items-center space-x-1 md:space-x-3">
            <button
              @click="navigateToPreviousLecture"
              class="p-1.5 md:p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!hasPreviousLecture"
              aria-label="Previous lecture"
            >
              <span class="material-symbols-outlined">navigate_before</span>
            </button>
            
            <div class="hidden sm:flex text-sm items-center px-2">
              <span class="text-gray-700 dark:text-gray-300">{{ currentLectureIndex + 1 }}/{{ totalLectureCount }}</span>
            </div>
            
            <button
              @click="navigateToNextLecture"
              class="p-1.5 md:p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!hasNextLecture"
              aria-label="Next lecture"
            >
              <span class="material-symbols-outlined">navigate_next</span>
            </button>
            
            <button
              v-if="!isLectureCompleted"
              @click="markLectureComplete"
              class="hidden sm:flex items-center px-3 py-1.5 bg-primary text-white rounded hover:bg-primary-dark transition-colors text-sm font-medium gap-x-1"
            >
              <span class="material-symbols-outlined text-sm">check_circle</span>
              <span>Mark complete</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <div class="w-16 h-16 border-4 border-t-transparent border-maroon-500 rounded-full animate-spin mx-auto"></div>
          <p class="mt-4 text-slate-500">Loading lecture content...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex-1 flex items-center justify-center">
        <div class="text-center max-w-md p-6">
          <span class="material-symbols-outlined text-5xl text-red-500">error</span>
          <h2 class="mt-4 text-xl font-bold text-slate-900">Something went wrong</h2>
          <p class="mt-2 text-slate-600">{{ errorMessage }}</p>
          <button 
            @click="fetchLectureData" 
            class="mt-4 px-4 py-2 bg-maroon-500 text-white rounded-lg hover:bg-maroon-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Content when loaded -->
      <div v-else-if="currentLecture" class="flex-1 overflow-hidden flex flex-col lg:flex-row">
        <!-- Lecture Video and Content -->
        <div class="w-full lg:w-2/3 h-full flex flex-col overflow-auto">
          <!-- Video Player -->
          <div class="w-full bg-gray-900">
            <CourseVideoPlayer 
              v-if="currentLecture.video_url" 
              :videoUrl="currentLecture.video_url" 
              :poster-image="currentLecture.thumbnailUrl"
              @video-error="handleVideoError"
              @video-complete="handleVideoComplete"
              @time-update="handleVideoTimeUpdate"
            />
            <div v-else class="aspect-video flex items-center justify-center bg-gray-800 text-white">
              <p>No video available for this lecture</p>
            </div>
          </div>

          <!-- Lecture Content -->
          <div class="flex-1 overflow-auto p-4">
            <CourseLectureContent 
              v-if="currentLecture" 
              :lecture="currentLecture"
            />
            
            <!-- Mobile Navigation Controls -->
            <div class="flex lg:hidden items-center justify-between mt-8 mb-4 border-t pt-4 border-gray-200 dark:border-gray-700">
              <button
                @click="navigateToPreviousLecture"
                class="flex items-center space-x-1 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 disabled:opacity-50"
                :disabled="!hasPreviousLecture"
              >
                <span class="material-symbols-outlined">chevron_left</span>
                <span>Previous</span>
              </button>
              
              <button
                v-if="!isLectureCompleted"
                @click="markLectureComplete"
                class="flex items-center space-x-1 px-3 py-2 rounded-lg bg-primary text-white"
              >
                <span class="material-symbols-outlined">check_circle</span>
                <span>Complete</span>
              </button>
              
              <button
                @click="navigateToNextLecture"
                class="flex items-center space-x-1 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 disabled:opacity-50"
                :disabled="!hasNextLecture"
              >
                <span>Next</span>
                <span class="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Notes Panel -->
        <div class="w-full lg:w-1/3 border-l border-gray-200 dark:border-gray-700 h-full overflow-auto">
          <LectureNotes 
            v-if="currentLecture" 
            :lectureId="currentLecture.id" 
            :courseId="courseId"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import CourseSideNav from '@/components/course/CourseSideNav.vue';
import CourseVideoPlayer from '@/components/course/CourseVideoPlayer.vue';
import CourseLectureContent from '@/components/course/CourseLectureContent.vue';
import LectureNotes from '@/components/course/LectureNotes.vue';

export default {
  components: {
    CourseSideNav,
    CourseVideoPlayer,
    CourseLectureContent,
    LectureNotes,
  },
  props: {
    courseId: {
      type: String,
      required: true
    },
    lectureId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter();
    const route = useRoute();
    
    // Define reactive state variables
    const loading = ref(true);
    const error = ref(false);
    const errorMessage = ref('');
    const sidebarOpen = ref(window.innerWidth >= 1024); // Default: open on desktop, closed on mobile
    const course = ref(null);
    const currentLecture = ref(null);
    const completedLectures = ref([]);
    const videoProgress = ref(0);
    const isLectureCompleted = ref(false);
    
    // Computed properties
    const courseWeeks = computed(() => {
      if (!course.value || !course.value.weeks) return [];
      return course.value.weeks;
    });
    
    const totalLectureCount = computed(() => {
      if (!courseWeeks.value) return 0;
      return courseWeeks.value.reduce((total, week) => {
        return total + (week.lectures ? week.lectures.length : 0);
      }, 0);
    });
    
    // Current lecture index and navigation
    const flattenedLectures = computed(() => {
      if (!courseWeeks.value) return [];
      return courseWeeks.value.reduce((lectures, week) => {
        if (week.lectures) {
          lectures.push(...week.lectures);
        }
        return lectures;
      }, []);
    });
    
    const currentLectureIndex = computed(() => {
      if (!currentLecture.value || !flattenedLectures.value.length) return -1;
      return flattenedLectures.value.findIndex(lecture => lecture.id === currentLecture.value.id);
    });
    
    const hasPreviousLecture = computed(() => {
      return currentLectureIndex.value > 0;
    });
    
    const hasNextLecture = computed(() => {
      return currentLectureIndex.value < flattenedLectures.value.length - 1;
    });
    
    // Get week name for current lecture
    const getCurrentWeekName = () => {
      if (!courseWeeks.value || !currentLecture.value) return '';
      
      for (let i = 0; i < courseWeeks.value.length; i++) {
        const week = courseWeeks.value[i];
        if (week.lectures.some(lecture => lecture.id === currentLecture.value.id)) {
          return `Week ${i + 1}`;
        }
      }
      
      return '';
    };
    
    // Navigation methods
    const navigateToPreviousLecture = () => {
      if (!hasPreviousLecture.value) return;
      
      const previousLecture = flattenedLectures.value[currentLectureIndex.value - 1];
      navigateToLecture(previousLecture.id);
    };
    
    const navigateToNextLecture = () => {
      if (!hasNextLecture.value) return;
      
      const nextLecture = flattenedLectures.value[currentLectureIndex.value + 1];
      navigateToLecture(nextLecture.id);
    };
    
    const navigateToLecture = (lectureId) => {
      router.push({
        name: 'CourseLecture',
        params: {
          courseId: props.courseId,
          lectureId: lectureId
        }
      });
    };
    
    const handleLectureSelection = (lecture) => {
      if (lecture && lecture.id) {
        navigateToLecture(lecture.id);
      }
    };
    
    // Fetch course and lecture data
    const fetchLectureData = async () => {
      loading.value = true;
      error.value = false;
      errorMessage.value = '';
      
      try {
        // Fetch course details
        const courseResponse = await fetch(`/api/v1/courses/${props.courseId}`);
        if (!courseResponse.ok) {
          throw new Error(`Failed to fetch course: ${courseResponse.statusText}`);
        }
        
        course.value = await courseResponse.json();
        
        // Fetch lecture details
        const lectureResponse = await fetch(`/api/v1/courses/${props.courseId}/lectures/${props.lectureId}`);
        if (!lectureResponse.ok) {
          throw new Error(`Failed to fetch lecture: ${lectureResponse.statusText}`);
        }
        
        currentLecture.value = await lectureResponse.json();
        
        // Fetch completed lectures
        try {
          const progressResponse = await fetch(`/api/v1/courses/${props.courseId}/progress`);
          if (progressResponse.ok) {
            const progressData = await progressResponse.json();
            completedLectures.value = progressData.completed_lectures || [];
            
            // Check if current lecture is completed
            isLectureCompleted.value = completedLectures.value.includes(props.lectureId);
          }
        } catch (progressErr) {
          console.warn('Failed to fetch progress:', progressErr);
          // Non-critical error, don't show to user
        }
        
        // Update user progress (optional)
        try {
          await fetch(`/api/v1/courses/${props.courseId}/lectures/${props.lectureId}/progress`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          });
        } catch (progressErr) {
          console.warn('Failed to update progress:', progressErr);
          // Non-critical error, don't show to user
        }
        
      } catch (err) {
        console.error('Error loading lecture data:', err);
        error.value = true;
        errorMessage.value = err.message || 'Failed to load course data';
      } finally {
        loading.value = false;
      }
    };
    
    // Mark lecture as complete
    const markLectureComplete = async () => {
      if (!currentLecture.value || isLectureCompleted.value) return;
      
      try {
        const response = await fetch(`/api/v1/courses/${props.courseId}/lectures/${props.lectureId}/complete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          isLectureCompleted.value = true;
          
          // Add to completed lectures if not already there
          if (!completedLectures.value.includes(props.lectureId)) {
            completedLectures.value.push(props.lectureId);
          }
        }
      } catch (err) {
        console.error('Failed to mark lecture as complete:', err);
      }
    };

    // Add video handlers
    const handleVideoError = (errMsg) => {
      console.error('Video error:', errMsg);
      // We don't set overall error state since we can still show lecture content
      // Just log it for monitoring
    };
    
    const handleVideoComplete = () => {
      // Auto-mark as complete when video is finished
      if (!isLectureCompleted.value) {
        markLectureComplete();
      }
    };
    
    const handleVideoTimeUpdate = (time) => {
      videoProgress.value = time;
    };

    // Toggle sidebar function
    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value;
    };
    
    // Watch for URL param changes
    watch(() => props.lectureId, (newLectureId, oldLectureId) => {
      if (newLectureId !== oldLectureId) {
        fetchLectureData();
      }
    });

    // Add responsive behavior
    onMounted(() => {
      // Fetch data when component mounts
      fetchLectureData();
      
      const handleResize = () => {
        if (window.innerWidth < 1024 && sidebarOpen.value) {
          sidebarOpen.value = false;
        }
      };
      
      window.addEventListener('resize', handleResize);
      
      return () => {
        window.removeEventListener('resize', handleResize);
      };
    });

    return {
      loading,
      error,
      errorMessage,
      sidebarOpen,
      course,
      currentLecture,
      completedLectures,
      videoProgress,
      isLectureCompleted,
      courseWeeks,
      totalLectureCount,
      currentLectureIndex,
      hasPreviousLecture,
      hasNextLecture,
      fetchLectureData,
      handleVideoError,
      handleVideoComplete,
      handleVideoTimeUpdate,
      toggleSidebar,
      navigateToPreviousLecture,
      navigateToNextLecture,
      markLectureComplete,
      handleLectureSelection,
      getCurrentWeekName
    };
  },
};
</script>

<style scoped>
/* Material symbol styles moved to main.css */
</style>