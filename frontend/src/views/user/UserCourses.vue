<script>
import SideNavBar from '../../layouts/SideNavBar.vue'
import ChatBotBox from '../../components/ChatBotBox.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { Course } from '@/models/Course'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import ChatBotWrapper from '@/components/ChatBotWrapper.vue'
import miniLoader from '@/components/common/miniLoader.vue'
const dummyAvatar =
  'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=='

export default {
  data() {
    return {
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      filters: ['All', 'In Progress', 'Completed', 'Bookmarked'],
      activeFilters: ['All'],
      selectedCourse: null,
      isCourseEnrolledDataLoading: false,
      // courses: [
      //   {
      //     id: 1,
      //     title: 'Introduction to Python Programming',
      //     description:
      //       'Learn Python basics and programming fundamentals through hands-on projects and exercises.',
      //     image: 'https://placehold.co/400x300',
      //     level: 'Beginner',
      //     duration: '8 weeks',
      //     progress: 75,
      //     isBookmarked: true,
      //     instructor: {
      //       name: 'Dr. Sarah Johnson',
      //       avatar: 'https://placehold.co/100x100',
      //     },
      //     videoUrl: 'https://www.youtube.com/embed/example',
      //     learningObjectives: [
      //       'Understand Python syntax and basic concepts',
      //       'Work with data structures and algorithms',
      //       'Build simple applications',
      //       'Debug and test code effectively',
      //     ],
      //     modules: [
      //       {
      //         title: 'Getting Started with Python',
      //         duration: '1h 30m',
      //         completed: true,
      //       },
      //       {
      //         title: 'Data Types and Variables',
      //         duration: '2h 15m',
      //         completed: true,
      //       },
      //       {
      //         title: 'Control Flow and Functions',
      //         duration: '2h 45m',
      //         completed: false,
      //       },
      //     ],
      //   },
      //   {
      //     id: 2,
      //     title: 'Web Development Fundamentals',
      //     description: 'Master HTML, CSS, and JavaScript to build modern responsive websites.',
      //     image: 'https://placehold.co/400x300',
      //     level: 'Intermediate',
      //     duration: '10 weeks',
      //     progress: 30,
      //     isBookmarked: false,
      //     instructor: {
      //       name: 'Alex Chen',
      //       avatar: 'https://placehold.co/100x100',
      //     },
      //   },
      //   {
      //     id: 3,
      //     title: 'Machine Learning Essentials',
      //     description: 'Explore the fundamentals of machine learning and AI applications.',
      //     image: 'https://placehold.co/400x300',
      //     level: 'Advanced',
      //     duration: '12 weeks',
      //     progress: 15,
      //     isBookmarked: true,
      //     instructor: {
      //       name: 'Dr. Michael Brown',
      //       avatar: 'https://placehold.co/100x100',
      //     },
      //   },
      // ],
      courses: [],
      modules: [],
      isBookmarking: false,
    }
  },
  components: {
    SideNavBar,
    ChatBotBox,
    LoadingSpinner,
    ChatBotWrapper,
    miniLoader,
  },
  computed: {
    filteredCourses() {
      let filtered = [...this.courses]

      // Apply search filter with debouncing
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter((course) => {
          const searchableFields = [
            course.title,
            course.description,
            course.instructor.name,
            course.level,
            ...(course.learningObjectives || []),
            ...(course.modules?.map((m) => m.title) || []),
          ]

          return searchableFields.some((field) => field.toLowerCase().includes(query))
        })

        // Sort results by relevance
        filtered.sort((a, b) => {
          const aTitle = a.title.toLowerCase()
          const bTitle = b.title.toLowerCase()
          const aStartsWithQuery = aTitle.startsWith(query)
          const bStartsWithQuery = bTitle.startsWith(query)

          if (aStartsWithQuery && !bStartsWithQuery) return -1
          if (!aStartsWithQuery && bStartsWithQuery) return 1
          return 0
        })
      }

      // Apply status filters
      if (!this.activeFilters.includes('All')) {
        filtered = filtered.filter((course) => {
          const matchesInProgress =
            this.activeFilters.includes('In Progress') &&
            course.progress > 0 &&
            course.progress < 100
          const matchesCompleted =
            this.activeFilters.includes('Completed') && course.progress === 100
          const matchesBookmarked = this.activeFilters.includes('Bookmarked') && course.isBookmarked

          return matchesInProgress || matchesCompleted || matchesBookmarked
        })
      }

      return filtered
    },
  },
  watch: {
    searchQuery: {
      handler(newQuery) {
        if (this.searchTimeout) {
          clearTimeout(this.searchTimeout)
        }
        this.isSearching = true

        this.searchTimeout = setTimeout(() => {
          this.isSearching = false
        }, 300)
      },
    },
  },
  methods: {
    showSuccessToast(msg) {
      const toast = useToast() // Call inside the method
      toast.success(msg, { timeout: 3000 })
    },
    showErrorToast(error, defaultMessage) {
      const toast = useToast()
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    },
    toggleFilter(filter) {
      if (filter === 'All') {
        this.activeFilters = ['All']
      } else {
        // Remove 'All' if it exists
        this.activeFilters = this.activeFilters.filter((f) => f !== 'All')

        const index = this.activeFilters.indexOf(filter)
        if (index === -1) {
          // Add the filter
          this.activeFilters.push(filter)
        } else {
          // Remove the filter
          this.activeFilters.splice(index, 1)
        }

        // If no filters selected, default to 'All'
        if (this.activeFilters.length === 0) {
          this.activeFilters = ['All']
        }
      }
    },
    async toggleBookmark(course) {
      //API call to toggle the boomark status
      this.isBookmarking = true
      const data = {
        course_id: course.id,
        type: 'Course',
        title: course.title,
        author: course.instructor.name,
      }
      const token = localStorage.getItem('token') // Retrieve token from localStorage
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }

      try {
        const response = await api.post('/user/bookmarked-materials', { ...data }, headers)
        if (response.status == 200) {
          this.showSuccessToast('Course bookmarked successfully')
          course.isBookmarked = !course.isBookmarked
        } else {
          throw new Error('Bookmarking failed. Try Again...')
        }
      } catch (error) {
        this.showErrorToast(error, 'Bookmarking failed. Try Again...')
        console.error('Error bookmarking the courses:', error)
      } finally {
        this.isBookmarking = false
      }
      // If we're filtering by bookmarked, update the view
      if (this.activeFilters.includes('Bookmarked')) {
        this.$forceUpdate()
      }
    },
    continueCourse(course) {
      this.$router.push({
        name: 'CourseLectureView',
        params: { courseId: course.id },
      })
    },

    //APIs
    async getUserEnrolledCourses() {
      try {
        this.isCourseEnrolledDataLoading = true
        const token = localStorage.getItem('token') // Retrieve token from localStorage
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        const response = await api.get('/user/courses', headers)
        if (response.status !== 200) {
          this.showErrorToast('Failed to fetch user course data')
          throw new Error('Failed to fetch user course data')
        }
        response.data.forEach((c) => {
          const course = new Course({
            id: c.id,
            title: c.title,
            description: c.description,
            status: c.status,
            // progress: 50,
            level: c.level,
            duration: c.duration + ' Weeks',
            studentsCount: 100,
            is_bookmarked: c.is_bookmarked,
            instructor: { name: c.created_by, avatar: dummyAvatar },
          })
          this.courses.push(course)
        })
        this.isCourseEnrolledDataLoading = false
        this.showSuccessToast('Course data fetched successfully')
      } catch (error) {
        this.isCourseEnrolledDataLoading = false
        this.showErrorToast(error, 'Failed to Load course data')
      }
    },
  },
  mounted() {
    this.getUserEnrolledCourses()
  },
  watch: {
    $route(to, from) {
      if (to.path === from.path) {
        this.getUserEnrolledCourses() // Reload data when the same route is clicked
      }
    },
  },
}
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 p-6 overflow-y-auto">
      <!-- Course Header -->
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-800">My Courses</h1>
            <p class="text-gray-600">Continue your learning journey</p>
          </div>
          <div class="flex space-x-4">
            <div class="relative">
              <input
                type="text"
                placeholder="Search courses..."
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
                v-model="searchQuery"
                @focus="isSearching = true"
                @blur="isSearching = false"
              />
              <i
                class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              ></i>
              <div
                v-if="isSearching && searchQuery"
                class="absolute w-full bg-white mt-1 rounded-lg shadow-lg border border-gray-200 z-10"
              >
                <div class="p-2 text-sm text-gray-500" v-if="filteredCourses.length === 0">
                  No results found
                </div>
                <div v-else class="max-h-64 overflow-y-auto">
                  <div
                    v-for="course in filteredCourses"
                    :key="course.id"
                    class="p-2 hover:bg-gray-50 cursor-pointer"
                    @click="selectedCourse = course"
                  >
                    <div class="font-medium text-gray-800">{{ course.title }}</div>
                    <div class="text-sm text-gray-500">{{ course.instructor.name }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex space-x-2">
              <button
                v-for="filter in filters"
                :key="filter"
                @click="toggleFilter(filter)"
                :class="[
                  'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  activeFilters.includes(filter)
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
                ]"
              >
                {{ filter }}
              </button>
            </div>
          </div>
        </div>

        <!-- Course Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div
            v-for="course in filteredCourses"
            :key="course.id"
            class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
          >
            <div class="relative">
              <img :src="course.image" :alt="course.title" class="w-full h-48 object-cover" />
              <div class="absolute top-4 right-4">
                <button
                  :disabled="course.isBookmarked"
                  @click="toggleBookmark(course)"
                  class="p-2 rounded-full bg-white shadow-md hover:bg-gray-50"
                >
                  <i
                    :class="[
                      'fas',
                      course.isBookmarked
                        ? 'fa-bookmark text-blue-900'
                        : 'fa-bookmark text-gray-400',
                    ]"
                  ></i>
                </button>
              </div>
            </div>
            <div class="p-6">
              <div class="flex items-center justify-between mb-2">
                <span
                  :class="[
                    'px-3 py-1 rounded-full text-sm font-medium',
                    course.level === 'Beginner'
                      ? 'bg-green-100 text-green-800'
                      : course.level === 'Intermediate'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800',
                  ]"
                >
                  {{ course.level }}
                </span>
                <span class="text-gray-600 text-sm">{{ course.duration }}</span>
              </div>
              <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ course.title }}</h3>
              <p class="text-gray-600 text-sm mb-4">{{ course.description }}</p>
              <!-- Course progress -->
              <!-- <div class="space-y-3">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-600">Progress</span>
                  <span class="font-medium">{{ course.progress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    :style="{ width: `${course.progress}%` }"
                  ></div>
                </div>
              </div> -->
              <div class="mt-4 flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <img
                    :src="course.instructor.avatar"
                    :alt="course.instructor.name"
                    class="w-8 h-8 rounded-full object-cover"
                  />
                  <span class="text-sm text-gray-600">{{ course.instructor.name }}</span>
                </div>
                <button
                  @click="continueCourse(course)"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Continue
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Course Content (when a course is selected) -->
        <div v-if="selectedCourse" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center space-x-4">
              <button @click="selectedCourse = null" class="text-gray-600 hover:text-gray-800">
                <i class="fas fa-arrow-left"></i>
              </button>
              <h2 class="text-xl font-semibold text-gray-800">{{ selectedCourse.title }}</h2>
            </div>
            <div class="flex items-center space-x-4">
              <button class="text-gray-600 hover:text-gray-800">
                <i class="fas fa-download"></i>
              </button>
              <button class="text-gray-600 hover:text-gray-800">
                <i class="fas fa-share"></i>
              </button>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-6">
            <!-- Course Content -->
            <div class="col-span-2">
              <div class="aspect-w-16 aspect-h-9 mb-6">
                <iframe
                  :src="selectedCourse.videoUrl"
                  class="w-full h-full rounded-lg"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                >
                </iframe>
              </div>
              <div class="space-y-4">
                <div>
                  <h3 class="text-lg font-semibold text-gray-800 mb-2">About this course</h3>
                  <p class="text-gray-600">{{ selectedCourse.description }}</p>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-800 mb-2">What you'll learn</h3>
                  <ul class="grid grid-cols-2 gap-2">
                    <li
                      v-for="(objective, index) in selectedCourse.learningObjectives"
                      :key="index"
                      class="flex items-start space-x-2"
                    >
                      <i class="fas fa-check text-green-500 mt-1"></i>
                      <span class="text-gray-600">{{ objective }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Course Modules -->
            <div class="col-span-1">
              <div class="bg-gray-50 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Course Content</h3>
                <div class="space-y-2">
                  <div
                    v-for="(module, index) in selectedCourse.modules"
                    :key="index"
                    class="bg-white rounded-lg p-4 cursor-pointer hover:bg-gray-50"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <h4 class="font-medium text-gray-800">{{ module.title }}</h4>
                      <span class="text-sm text-gray-600">{{ module.duration }}</span>
                    </div>
                    <div class="flex items-center space-x-2 text-sm text-gray-600">
                      <i
                        :class="[
                          'fas',
                          module.completed
                            ? 'fa-check-circle text-green-500'
                            : 'fa-circle text-gray-400',
                        ]"
                      ></i>
                      <span>{{ module.completed ? 'Completed' : 'Not completed' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Loading Overlay -->
  <div v-if="isCourseEnrolledDataLoading" class="loading-overlay">
    <LoadingSpinner />
  </div>
  <div
    v-if="isBookmarking"
    class="fixed top-[140px] left-1/2 transform -translate-x-1/2 bg-opacity-50 z-50 bg-gray-200 px-2 py-4 rounded-md"
  >
    <miniLoader>Bookmarking in progress...</miniLoader>
  </div>
</template>

<style scoped>
.aspect-w-16 {
  position: relative;
  padding-bottom: 56.25%;
}

.aspect-w-16 iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

input:focus {
  outline: none;
}
.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
