<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 p-6 overflow-y-auto">
      <div class="max-w-7xl mx-auto">
        <!-- Header with Academic Progress -->
        <div class="mb-8">
          <div class="flex justify-between items-center mb-4">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Course History</h1>
              <p class="text-gray-600 mt-1">Track your academic journey and achievements</p>
            </div>
            <div class="text-right">
              <div class="flex items-center">
                <div class="text-2xl font-bold text-gray-900 mr-2">{{ completedCoursesOnly.length }}</div>
                <div class="flex flex-col">
                  <div class="text-sm text-gray-600">Completed</div>
                  <div class="text-xs text-gray-500">of {{ totalEnrolled }} enrolled</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex flex-wrap items-center justify-between text-sm mb-2">
              <span class="font-medium text-gray-900">Academic Progress</span>
              <div class="flex space-x-4">
                <span class="text-gray-600">
                  <span class="font-medium">{{ completedCoursesOnly.length }}</span> Completed
                </span>
                <span class="text-gray-600">
                  <span class="font-medium">{{ inProgressCourses.length }}</span> In Progress
                </span>
                <span class="text-blue-600 font-medium">{{ completionRate }}% Complete</span>
              </div>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-2.5">
              <div
                class="bg-maroon-600 h-2.5 rounded-full transition-all duration-500"
                :style="{ width: `${completionRate}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-maroon-50 rounded-lg mr-4">
              <span class="material-icons text-maroon-600">school</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ totalCredits }}</div>
              <div class="text-sm text-gray-600">Credits Earned</div>
            </div>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-blue-50 rounded-lg mr-4">
              <span class="material-icons text-blue-600">verified</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ certificatesCount }}</div>
              <div class="text-sm text-gray-600">Certificates Earned</div>
            </div>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-green-50 rounded-lg mr-4">
              <span class="material-icons text-green-600">grade</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ averageGrade }}</div>
              <div class="text-sm text-gray-600">Average Grade</div>
            </div>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center">
            <div class="p-3 bg-purple-50 rounded-lg mr-4">
              <span class="material-icons text-purple-600">trending_up</span>
            </div>
            <div>
              <div class="text-2xl font-bold text-gray-900">{{ inProgressCourses.length }}</div>
              <div class="text-sm text-gray-600">In-Progress Courses</div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <div class="flex flex-wrap gap-6">
            <div class="flex-1 min-w-[250px]">
              <label class="block text-sm font-medium text-gray-900 mb-2">Search Courses</label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="material-icons text-gray-400 text-lg">search</span>
                </span>
                <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="Search by course name or instructor"
                  class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 placeholder-gray-500"
                />
              </div>
            </div>
            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-2">Sort By</label>
              <div class="relative">
                <select
                  v-model="sortBy"
                  class="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 appearance-none"
                >
                  <option value="date">Recent First</option>
                  <option value="name">Course Name</option>
                  <option value="grade">Highest Grade</option>
                  <option value="progress">Highest Progress</option>
                  <option value="credits">Most Credits</option>
                </select>
                <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="material-icons text-gray-400 text-lg">expand_more</span>
                </span>
              </div>
            </div>
            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-2">Course Filter</label>
              <div class="relative">
                <select
                  v-model="gradeFilter"
                  class="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 appearance-none"
                >
                  <option value="all">All Courses</option>
                  <option value="inprogress">In Progress</option>
                  <option value="A">A Grades (90-100)</option>
                  <option value="B">B Grades (80-89)</option>
                  <option value="C">C Grades (70-79)</option>
                  <option value="D">D Grades (60-69)</option>
                </select>
                <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span class="material-icons text-gray-400 text-lg">expand_more</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isDataLoading" class="flex justify-center py-12">
          <LoadingSpinner />
        </div>

        <!-- Error State -->
        <div v-else-if="hasError" class="text-center py-12 bg-white rounded-xl shadow-sm border border-red-100">
          <span class="material-icons text-red-500 text-4xl mb-2">error_outline</span>
          <div class="text-gray-800 font-medium mb-2">Failed to load your course history</div>
          <div class="text-gray-600 mb-4">{{ errorMessage }}</div>
          <button 
            @click="retry" 
            class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors inline-flex items-center"
          >
            <span class="material-icons text-sm mr-1">refresh</span>
            Try Again
          </button>
        </div>

        <!-- Course List -->
        <div v-else class="space-y-4">
          <div
            v-for="course in filteredCourses"
            :key="course.id"
            class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-4">
                  <h3 class="text-lg font-semibold text-gray-900">{{ course.name }}</h3>
                  <span
                    v-if="course.grade"
                    class="px-3 py-1 rounded-full text-sm font-medium flex items-center"
                    :class="getGradeClass(course.grade)"
                  >
                    <span class="material-icons text-sm mr-1">grade</span>
                    {{ course.grade }}
                  </span>
                  <span
                    v-else
                    class="px-3 py-1 rounded-full text-sm font-medium flex items-center bg-blue-50 text-blue-600"
                  >
                    <span class="material-icons text-sm mr-1">school</span>
                    {{ course.status || 'In Progress' }}
                  </span>
                </div>

                <p class="text-gray-700 mt-2">{{ course.description }}</p>

                <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">person</span>
                      Instructor
                    </div>
                    <div class="font-medium text-gray-900">{{ course.instructor }}</div>
                  </div>
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">event</span>
                      {{ course.completion_date ? 'Completed' : 'Enrolled' }}
                    </div>
                    <div class="font-medium text-gray-900">
                      {{ course.completion_date ? formatDate(course.completion_date) : formatDate(course.enrollment_date) }}
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">stars</span>
                      Credits
                    </div>
                    <div class="font-medium text-gray-900">{{ course.credits }}</div>
                  </div>
                  <div>
                    <div class="flex items-center text-sm text-gray-600 mb-1">
                      <span class="material-icons text-sm mr-1">verified</span>
                      Certificate
                    </div>
                    <a
                      v-if="course.certificate_url"
                      :href="course.certificate_url"
                      target="_blank"
                      class="text-maroon-600 hover:text-maroon-700 font-medium inline-flex items-center"
                    >
                      View Certificate
                      <span class="material-icons text-sm ml-1">open_in_new</span>
                    </a>
                    <span v-else class="text-gray-400">Not Available</span>
                  </div>
                </div>
                <!-- Display progress if course is in progress -->
                <div v-if="course.status !== 'COMPLETED' && course.progress !== null" class="mt-4">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="font-medium text-gray-700">Course Progress</span>
                    <span class="text-gray-600">{{ course.progress || 0 }}%</span>
                  </div>
                  <div class="w-full bg-gray-100 rounded-full h-2">
                    <div
                      class="bg-maroon-600 h-2 rounded-full transition-all duration-500"
                      :style="{ width: `${course.progress || 0}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div
            v-if="filteredCourses.length === 0"
            class="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100"
          >
            <span class="material-icons text-gray-400 text-4xl mb-2">search_off</span>
            <div class="text-gray-600">No courses found matching your criteria</div>
            <button
              @click="resetFilters"
              class="mt-4 text-maroon-600 hover:text-maroon-700 font-medium"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '@/layouts/SideNavBar.vue'
import api from '@/utils/api'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'CourseHistory',
  components: {
    SideNavBar,
    LoadingSpinner,
  },
  data() {
    return {
      isDataLoading: true,
      hasError: false,
      errorMessage: '',
      completedCourses: [],
      totalEnrolled: 0,
      searchQuery: '',
      sortBy: 'date',
      gradeFilter: 'all',
    }
  },
  computed: {
    filteredCourses() {
      let courses = [...this.completedCourses]

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        courses = courses.filter(
          (course) =>
            course.name.toLowerCase().includes(query) ||
            (course.instructor && course.instructor.toLowerCase().includes(query)) ||
            (course.description && course.description.toLowerCase().includes(query)),
        )
      }

      if (this.gradeFilter !== 'all') {
        if (this.gradeFilter === 'inprogress') {
          courses = courses.filter((course) => course.status !== 'COMPLETED')
        } else {
          courses = courses.filter((course) => 
            course.grade && course.grade.startsWith(this.gradeFilter)
          )
        }
      }

      courses.sort((a, b) => {
        switch (this.sortBy) {
          case 'date':
            // Sort by completion date first, then enrollment date
            const aDate = a.completion_date ? new Date(a.completion_date) : (a.enrollment_date ? new Date(a.enrollment_date) : new Date(0))
            const bDate = b.completion_date ? new Date(b.completion_date) : (b.enrollment_date ? new Date(b.enrollment_date) : new Date(0))
            return bDate - aDate
          case 'name':
            return a.name.localeCompare(b.name)
          case 'grade':
            return this.getGradeValue(b.grade) - this.getGradeValue(a.grade)
          case 'progress':
            return (b.progress || 0) - (a.progress || 0)
          case 'credits':
            return b.credits - a.credits
          default:
            return 0
        }
      })

      return courses
    },
    completedCoursesOnly() {
      return this.completedCourses.filter(course => course.status === 'COMPLETED')
    },
    inProgressCourses() {
      return this.completedCourses.filter(course => course.status !== 'COMPLETED')
    },
    averageGrade() {
      const completedWithGrades = this.completedCoursesOnly.filter(course => course.grade)
      if (completedWithGrades.length === 0) return 0
      const total = completedWithGrades.reduce(
        (sum, course) => sum + this.getGradeValue(course.grade),
        0,
      )
      return Math.round((total / completedWithGrades.length) * 10) / 10
    },
    totalCredits() {
      return this.completedCoursesOnly.reduce((sum, course) => sum + (course.credits || 0), 0)
    },
    completionRate() {
      return this.totalEnrolled ? Math.round((this.completedCoursesOnly.length / this.totalEnrolled) * 100) : 0
    },
    certificatesCount() {
      return this.completedCoursesOnly.filter((course) => course.certificate_url).length
    },
    currentSemesterGPA() {
      const currentSemester = 'Fall'
      const semesterCourses = this.completedCoursesOnly.filter(
        (course) => course.semester === currentSemester && course.grade,
      )

      if (semesterCourses.length === 0) return '0.00'

      const totalPoints = semesterCourses.reduce(
        (sum, course) => sum + this.getGradeValue(course.grade) * course.credits,
        0,
      )
      const totalCredits = semesterCourses.reduce((sum, course) => sum + course.credits, 0)

      return ((totalPoints / (totalCredits * 100)) * 4).toFixed(2)
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
    formatDate(date) {
      if (!date) {
        return 'Not completed yet';
      }
      const d = new Date(date);
      if (isNaN(d.getTime())) {
        return 'Invalid date';
      }
      const months = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
      ]
      return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
    },
    getGradeClass(grade) {
      if (!grade) {
        return 'bg-gray-100 text-gray-600'; // Default styling for no grade
      }
      const firstLetter = grade.charAt(0);
      switch (firstLetter) {
        case 'A':
          return 'bg-green-100 text-green-800'
        case 'B':
          return 'bg-blue-100 text-blue-800'
        case 'C':
          return 'bg-yellow-100 text-yellow-800'
        case 'D':
          return 'bg-orange-100 text-orange-800'
        default:
          return 'bg-red-100 text-red-800'
      }
    },
    getGradeValue(grade) {
      if (!grade) {
        return 0; // Default value when no grade is available
      }
      const gradeValues = {
        'A+': 100,
        A: 95,
        'A-': 90,
        'B+': 87,
        B: 83,
        'B-': 80,
        'C+': 77,
        C: 73,
        'C-': 70,
        'D+': 67,
        D: 63,
        'D-': 60,
        F: 0,
      }
      return gradeValues[grade] || 0
    },
    resetFilters() {
      this.searchQuery = ''
      this.sortBy = 'date'
      this.gradeFilter = 'all'
    },
    retry() {
      this.hasError = false;
      this.errorMessage = '';
      this.getCourseHistoryData();
    },
    async getCourseHistoryData() {
      try {
        this.isDataLoading = true;
        this.hasError = false;
        this.errorMessage = '';
        
        const token = localStorage.getItem('token')
        if (!token) {
          this.hasError = true;
          this.errorMessage = 'Authentication token not found. Please log in again.';
          throw new Error('No authentication token found');
        }

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`
          },
        }

        const response = await api.get('/user/courses/history', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user course data')
        
        this.completedCourses = response.data || []
        
        // Set total enrolled if data is available
        if (this.completedCourses.length > 0 && 
            this.completedCourses[0].hasOwnProperty('total_enrolled_course')) {
          this.totalEnrolled = this.completedCourses[0].total_enrolled_course
        } else {
          this.totalEnrolled = this.completedCourses.length
        }
        
        // Ensure all course objects have consistent property structure
        this.completedCourses = this.completedCourses.map(course => ({
          ...course,
          grade: course.grade || null,
          status: course.status || 'IN_PROGRESS',
          credits: course.credits || 0,
          progress: course.progress || 0
        }))
        
        this.showSuccessToast('Course history loaded successfully')
      } catch (error) {
        console.error('Error fetching course history:', error)
        this.completedCourses = [] // Reset to empty array on error
        this.totalEnrolled = 0
        this.hasError = true;
        this.errorMessage = error.message || 'Failed to fetch course history';
        this.showErrorToast(error, 'Failed to fetch course history')
      } finally {
        this.isDataLoading = false
      }
    },
  },
  mounted() {
    this.getCourseHistoryData()
  },
}
</script>

<style scoped>
.material-icons {
  font-size: inherit;
  line-height: inherit;
  vertical-align: middle;
}
.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
