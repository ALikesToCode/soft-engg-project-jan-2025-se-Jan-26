<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 overflow-y-auto">
      <div class="p-6">
        <div class="mb-6 flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Course Enrollment & Student Progress</h1>
            <p class="text-gray-800">Manage enrolled students and track their progress</p>
          </div>
          <button
            @click="showEnrollPopup = true"
            :disabled="selectedCourse === ''"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition flex items-center gap-2"
          >
            <span class="material-icons">add</span>
            Enroll Students
          </button>
          <!-- Enroll Course Popup -->
          <div
            v-if="showEnrollPopup"
            class="fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 z-20"
          >
            <div class="bg-white p-6 rounded-lg shadow-lg w-auto">
              <h2 class="text-xl font-semibold mb-4">
                Enroll Students in
                <span class="underline underline-offset-1">{{ selectedCourse.name }}</span> Course
              </h2>
              <label class="block text-sm font-medium text-gray-900 mb-2"
                >Enter Students Emails (comma-separated)</label
              >
              <textarea
                v-model="emailList"
                rows="3"
                class="w-full px-3 py-2 border rounded-md"
                placeholder="example1@gmail.com, example2@gmail.com"
              ></textarea>
              <div class="flex justify-end mt-4 gap-2">
                <button
                  @click="showEnrollPopup = false"
                  class="px-4 py-2 bg-gray-400 text-gray-100 rounded-md"
                >
                  Cancel
                </button>
                <button
                  :disabled="emailList === ''"
                  @click="enrollStudents"
                  class="px-4 py-2 bg-maroon-600 text-white rounded-md hover:bg-maroon-700"
                >
                  Enroll
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="bg-white p-4 rounded-lg shadow mb-6">
          <div class="flex flex-wrap gap-4">
            <!-- Course Dropdown -->
            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-1">Select Course</label>
              <select
                v-model="selectedCourse"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option disabled value="">Select a Course</option>
                <option v-for="course in facultyCourses" :key="course.id" :value="course">
                  {{ course.name }}
                </option>
              </select>
            </div>

            <!-- Search Students -->
            <div class="flex-1 min-w-[200px]">
              <label class="block text-sm font-medium text-gray-900 mb-1">Search Students</label>
              <input
                :disabled="selectedCourse === ''"
                v-model="searchQuery"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Search by name or email..."
              />
            </div>

            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-1">Progress Filter</label>
              <select
                v-model="progressFilter"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="all">All Progress</option>
                <option value="high">High (>75%)</option>
                <option value="medium">Medium (25-75%)</option>
                <option value="low">Low (<25%)</option>
              </select>
            </div>

            <div class="w-48">
              <label class="block text-sm font-medium text-gray-900 mb-1">Sort By</label>
              <select v-model="sortBy" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                <option value="name">Name</option>
                <option value="progress">Progress</option>
                <option value="enrollment">Enrollment Date</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Student List -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="flex justify-between items-center p-4 border-b">
            <h2 class="text-lg font-semibold text-gray-900">Enrolled Students</h2>
            <button
              :disabled="students.length === 0"
              @click="exportData"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center gap-2"
            >
              <span class="material-icons">download</span>
              Export Data
            </button>
          </div>

          <div v-if="students.length != 0" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider"
                  >
                    Student
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider"
                  >
                    Progress
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider"
                  >
                    Assignments
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider"
                  >
                    Last Active
                  </th>
                  <th
                    class="px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider"
                  >
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="student in filteredStudents" :key="student.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <img
                          :src="student.picture"
                          referrerpolicy="no-referrer"
                          class="h-10 w-10 rounded-full"
                          alt=""
                        />
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ student.name }}</div>
                        <div class="text-sm text-gray-800">{{ student.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        class="bg-blue-600 h-2.5 rounded-full"
                        :style="{ width: student.progress + '%' }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-900">{{ student.progress }}%</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-900"
                      >{{ student.completedAssignments }}/{{ student.totalAssignments }}</span
                    >
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-800">
                    {{ student.last_activity }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      @click="deleteEnrollment(student)"
                      class="text-red-600 hover:text-red-800 flex items-center gap-1"
                    >
                      <span class="material-icons">delete</span>
                      Delete Enrollment
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            v-if="selectedCourse === ''"
            class="flex flex-col items-center justify-center text-center h-full"
          >
            <p class="px-4 md:py-8 text-gray-800 font-semibold text-xl">
              Please select a course to view the enrollments
            </p>
          </div>
          <div
            v-else-if="students.length === 0"
            class="flex flex-col items-center justify-center text-center h-full"
          >
            <p class="p-4 text-gray-800 font-semibold text-xl">
              No students enrolled in this course
            </p>
            <button
              @click="showEnrollPopup = true"
              :disabled="selectedCourse === ''"
              class="px-4 py-2 mb-4 bg-green-600 text-white rounded-md hover:bg-green-700 transition flex items-center gap-2"
            >
              <span class="material-icons">add</span>
              Enroll Now
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Loading Overlay -->
  <div v-if="loading" class="loading-overlay">
    <LoadingSpinner />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import api from '@/utils/api'
import SideNavBar from '@/layouts/SideNavBar.vue'
import { useCourseStore } from '@/stores/courseStore'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

import { useToast } from 'vue-toastification'

export default {
  name: 'CourseEnrollmentView',
  components: {
    SideNavBar,
    LoadingSpinner,
  },
  setup() {
    const route = useRoute()
    const courseId = ref('')
    const students = ref([])
    const searchQuery = ref('')
    const progressFilter = ref('all')
    const sortBy = ref('name')
    const currentPage = ref(1)
    const itemsPerPage = 10
    const totalStudents = ref(0)
    const loading = ref(false)

    const courseStore = useCourseStore()
    const selectedCourse = ref('')
    const facultyCourses = ref([
      // { id: 'course1', name: 'Introduction to Programming' }
    ])
    const showEnrollPopup = ref(false)
    const emailList = ref('')

    const toast = useToast()

    const showSuccessToast = (res, defaultMsg) => {
      const msg = res.response?.data?.message || defaultMsg
      toast.success(msg)
    }

    const showErrorToast = (error, defaultMsg) => {
      const msg = error.response?.data?.message || defaultMsg
      toast.error(msg)
    }

    // Fetch students and their progress
    const fetchStudents = async () => {
      try {
        console.log('Fetching students for course:', courseId.value)
        if (!courseId.value) return
        loading.value = true
        // const [studentsResponse, progressResponse] = await Promise.all([
        //   api.get('/courses/' + courseId.value + '/students'),
        //   api.get('/courses/' + courseId.value + '/progress'),
        // ])
        const studentsResponse = await api.get('/courses/' + courseId.value + '/students')
        const progressResponse = await api.get('/courses/' + courseId.value + '/progress')

        // Combine student data with progress data
        students.value = studentsResponse.data.map((student) => ({
          ...student,
          progress: progressResponse.data.find((p) => p.studentId === student.id)?.progress || 0,
        }))
        console.log('Fetched students:', students.value)

        totalStudents.value = students.value.length
        showSuccessToast(studentsResponse, 'Students Data loaded successfully')
      } catch (error) {
        showErrorToast(error, 'Failed to load students data')
        console.error('Error fetching student data:', error)
      } finally {
        loading.value = false
      }
    }

    const getFacultyCourses = async () => {
      try {
        loading.value = true
        const response = await courseStore.getFacultyCourses()
        response.data.forEach((course) => {
          facultyCourses.value.push({
            id: course.id,
            name: course.name,
          })
        })
        facultyCourses.value = response.data
        showSuccessToast(response, 'Courses loaded successfully')
      } catch (error) {
        showErrorToast(error, 'Failed to load your courses')
      } finally {
        loading.value = false
      }
    }

    const enrollStudents = async () => {
      loading.value = true
      const emails = emailList.value.split(',').map((email) => email.trim())
      console.log('Enrolling students:', emails)
      if (!courseId.value) return
      if (!emails.length) return
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
            'Content-Type': 'application/json', // Ensure JSON format
          },
        }

        const payload = {
          course_id: courseId.value, // Course ID
          student_emails: emails, // Sending emails as an array
        }
        const response = await api.post('/courses/enroll', payload, headers)
        showSuccessToast(response, 'Students enrolled successfully')
      } catch (error) {
        showErrorToast(error, 'Failed to enroll students. Try Again')
      } finally {
        loading.value = false
        showEnrollPopup.value = false
        emailList.value = ''
      }
    }

    const deleteEnrollment = async (student) => {
      if (!courseId.value) return
      if (!student.id) return
      try {
        loading.value = true
        const response = await api.delete(`/courses/${courseId.value}/student/${student.id}`)
        students.value = students.value.filter((s) => s.id !== student.id)
        showSuccessToast(response, 'Student enrollment deleted successfully')
        fetchStudents()
      } catch (error) {
        showErrorToast(error, 'Failed to delete student enrollment')
      } finally {
        loading.value = false
      }
    }

    // Computed properties for filtering and sorting
    const filteredStudents = computed(() => {
      let filtered = [...students.value]

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(
          (student) =>
            student.name.toLowerCase().includes(query) ||
            student.email.toLowerCase().includes(query),
        )
      }

      // Apply progress filter
      if (progressFilter.value !== 'all') {
        filtered = filtered.filter((student) => {
          const progress = student.progress
          switch (progressFilter.value) {
            case 'high':
              return progress > 75
            case 'medium':
              return progress >= 25 && progress <= 75
            case 'low':
              return progress < 25
            default:
              return true
          }
        })
      }

      // Apply sorting
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'name':
            return a.name.localeCompare(b.name)
          case 'progress':
            return b.progress - a.progress
          case 'enrollment':
            return new Date(b.enrollmentDate) - new Date(a.enrollmentDate)
          default:
            return 0
        }
      })

      return filtered
    })

    // Pagination computed properties
    const paginatedStudents = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filteredStudents.value.slice(start, end)
    })

    const paginationStart = computed(() => (currentPage.value - 1) * itemsPerPage + 1)

    const paginationEnd = computed(() =>
      Math.min(currentPage.value * itemsPerPage, filteredStudents.value.length),
    )

    const isLastPage = computed(
      () => currentPage.value * itemsPerPage >= filteredStudents.value.length,
    )

    // Methods
    const exportData = () => {
      // Implementation for exporting data to CSV
      const csvContent =
        'data:text/csv;charset=utf-8,' +
        'Name,Email,Progress,Completed Assignments,Total Assignments\n' +
        filteredStudents.value
          .map(
            (student) =>
              student.name +
              ',' +
              student.email +
              ',' +
              student.progress +
              '%,' +
              student.completedAssignments +
              ',' +
              student.totalAssignments,
          )
          .join('\n')

      const encodedUri = encodeURI(csvContent)
      const link = document.createElement('a')
      link.setAttribute('href', encodedUri)
      link.setAttribute('download', 'student_progress.csv')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    const viewDetails = (student) => {
      // Implementation for viewing detailed student progress
      console.log('Viewing details for student:', student.id)
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    }

    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    const nextPage = () => {
      if (!isLastPage.value) {
        currentPage.value++
      }
    }

    // Lifecycle hooks
    onMounted(() => {
      // fetchStudents()
      getFacultyCourses()
    })

    watch(selectedCourse, (newCourse) => {
      courseId.value = newCourse.id
      if (newCourse) fetchStudents()
    })

    return {
      students,
      searchQuery,
      progressFilter,
      sortBy,
      currentPage,
      filteredStudents,
      paginationStart,
      paginationEnd,
      isLastPage,
      loading,
      totalStudents,
      exportData,
      viewDetails,
      formatDate,
      previousPage,
      nextPage,

      fetchStudents,

      selectedCourse,
      facultyCourses,
      getFacultyCourses,
      showEnrollPopup,
      emailList,
      enrollStudents,
      deleteEnrollment,

      showSuccessToast,
      showErrorToast,
    }
  },
}
</script>
<style scoped>
.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
