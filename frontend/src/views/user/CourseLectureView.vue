<template>
  <div class="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <SideNavBar />
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Top Navigation -->
      <CourseTopNav 
        :course="currentCourse"
        :is-bookmarked="isBookmarked"
        @toggle-bookmark="toggleBookmark"
        @toggle-notes="toggleNotes"
      />

      <!-- Course Layout -->
      <div class="flex flex-1 overflow-hidden">
        <!-- Course Navigation -->
        <CourseSideNav 
          :weeks="weeks"
          :selected-lecture="selectedLecture"
          :completed-lectures="completedLectures"
          :total-lectures="totalLectures"
          @select-lecture="selectLecture"
        />

        <!-- Main Content Area -->
        <div class="flex-1 overflow-y-auto bg-gradient-to-b from-gray-50 to-white">
          <div class="p-6 max-w-6xl mx-auto">
            <div v-if="selectedLecture" class="space-y-8">
              <!-- Video Player -->
              <CourseVideoPlayer :video-url="selectedLecture.videoUrl" />

              <!-- Lecture Content -->
              <CourseLectureContent 
                :lecture="selectedLecture"
                :get-file-icon="getFileIcon"
                @mark-complete="markAsComplete"
              />
            </div>

            <!-- Empty State -->
            <div v-else class="h-full flex items-center justify-center">
              <div class="text-center max-w-md py-12 space-y-6">
                <div class="inline-flex p-6 bg-primary-50 rounded-2xl">
                  <i class="fas fa-video text-4xl text-primary-500 transform rotate-12"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-900">Begin Your Learning Journey</h2>
                <p class="text-gray-600">Select a module from the curriculum to unlock knowledge</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '../../layouts/SideNavBar.vue'
import CourseTopNav from '../../components/course/CourseTopNav.vue'
import CourseSideNav from '../../components/course/CourseSideNav.vue'
import CourseVideoPlayer from '../../components/course/CourseVideoPlayer.vue'
import CourseLectureContent from '../../components/course/CourseLectureContent.vue'
import { useCourse } from '../../composables/useCourse'
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

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
      getFileIcon
    } = useCourse(courseId)

    onMounted(() => {
      document.documentElement.style.setProperty('--progress', currentCourse.value?.progress || 0)
    })

    return {
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
      getFileIcon
    }
  }
}
</script>

<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

:root {
  --primary-color: #8B0000;
  --primary-hover: #A52A2A;
  --text-primary: #1F2937;
  --text-secondary: #4B5563;
  --bg-primary: #FFFFFF;
  --bg-secondary: #F3F4F6;
  --bookmark-yellow: #FFD700;
}

.progress-ring circle {
  transition: stroke-dasharray 0.5s ease-out;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
}

/* Update color scheme */
.text-primary-600 {
  color: var(--primary-color) !important;
}

.bg-primary-500 {
  background-color: var(--primary-color) !important;
}

.bg-primary-50 {
  background-color: #FFF1F1 !important;
}

.hover\:bg-primary-600:hover {
  background-color: var(--primary-hover) !important;
}

.hover\:text-primary-600:hover {
  color: var(--primary-color) !important;
}

/* Responsive adjustments */
@media (max-width: 1280px) {
  .w-96 {
    width: 320px;
  }
}

@media (max-width: 1024px) {
  .flex-1.overflow-hidden.flex.flex-col {
    min-height: 100vh;
  }
  
  .flex.flex-1.overflow-hidden {
    flex-direction: column;
  }
  
  .w-full.lg\:w-80.xl\:w-96 {
    width: 100%;
    max-height: 300px;
  }
  
  .w-96.bg-white.border-l {
    width: 100%;
    height: 400px;
    border-left: none;
    border-top: 1px solid #E5E7EB;
  }
}

@media (max-width: 640px) {
  .px-4.sm\:px-6.py-4 {
    padding: 1rem;
  }
  
  .space-y-3.sm\:space-y-0 {
    margin-bottom: 1rem;
  }
  
  .flex.items-center.space-x-4.sm\:space-x-5 {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}

/* Video aspect ratio fix */
.aspect-w-16 {
  @apply relative overflow-hidden rounded-xl;
  padding-bottom: 56.25%;
} 

.aspect-w-16 > * {
  @apply absolute inset-0 w-full h-full object-cover;
}

/* Sidebar improvements */
.sidebar {
  @apply bg-white border-r border-gray-200;
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) #F3F4F6;
}

.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: #F3F4F6;
}

.sidebar::-webkit-scrollbar-thumb {
  background-color: var(--primary-color);
  border-radius: 3px;
}

/* Button and interaction improvements */
button {
  @apply transform transition-all duration-200 active:scale-95;
}

.shadow-gradient {
  box-shadow: 0 8px 32px rgba(139, 0, 0, 0.1);
}

/* Chat container */
.chat-container {
  height: calc(100vh - 4rem);
  overflow: hidden;
}

/* Progress bar improvements */
.bg-gradient-to-r {
  background: linear-gradient to right, var(--primary-color), var(--primary-hover));
}

/* Text colors */
.text-gray-900 {
  color: var(--text-primary);
}

.text-gray-600 {
  color: var(--text-secondary);
}

/* Active states */
.bg-primary-50.border-primary-200 {
  background-color: #FFF1F1 !important;
  border-color: #FECACA !important;
}

/* Bookmark icon color when bookmarked */
.fa-bookmark {
  color: var(--bookmark-yellow);
}
</style>