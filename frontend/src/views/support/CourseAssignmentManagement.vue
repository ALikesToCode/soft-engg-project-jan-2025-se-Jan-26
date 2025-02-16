<!-- Course Assignment Management for Technical Support -->
<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Side Navigation - Fixed position -->
    <div class="fixed inset-y-0 left-0">
      <SideNavBar />
    </div>
    
    <!-- Main Content Area - Scrollable with margin for sidebar -->
    <div class="flex-1 ml-16 overflow-auto">
      <div class="p-6">
        <!-- Header Section -->
        <header class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Course Assignment Management</h1>
          <p class="mt-2 text-gray-600">Manage faculty assignments and course enrollments</p>
        </header>

        <!-- Main Content -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <!-- Faculty Assignments Section -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-xl font-semibold text-gray-800">Faculty Assignments</h2>
              <div class="space-x-2">
                <button
                  @click="openBulkAssignModal"
                  class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  Bulk Assign
                </button>
                <button
                  @click="openAssignModal"
                  class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  New Assignment
                </button>
              </div>
            </div>

            <!-- Assignment List -->
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Faculty</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Students</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="assignment in assignments" :key="assignment.id">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ assignment.courseName }}</div>
                      <div class="text-sm text-gray-500">{{ assignment.courseCode }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ assignment.facultyName }}</div>
                      <div class="text-sm text-gray-500">{{ assignment.facultyEmail }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ assignment.enrolledStudents }}/{{ assignment.capacity }}</div>
                      <div class="text-sm text-gray-500">Enrolled</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="[
                          'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                          assignment.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        ]"
                      >
                        {{ assignment.status }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        @click="openEditModal(assignment)"
                        class="text-indigo-600 hover:text-indigo-900"
                      >
                        Edit
                      </button>
                      <button
                        @click="confirmRemoveAssignment(assignment)"
                        class="text-red-600 hover:text-red-900"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Course Statistics Section -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-6">Course Statistics</h2>
            <div class="space-y-6">
              <!-- Statistics Cards -->
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h3 class="text-sm font-medium text-gray-500">Total Courses</h3>
                  <p class="mt-1 text-2xl font-semibold text-gray-900">{{ statistics.totalCourses }}</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h3 class="text-sm font-medium text-gray-500">Active Faculty</h3>
                  <p class="mt-1 text-2xl font-semibold text-gray-900">{{ statistics.activeFaculty }}</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h3 class="text-sm font-medium text-gray-500">Total Students</h3>
                  <p class="mt-1 text-2xl font-semibold text-gray-900">{{ statistics.totalStudents }}</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h3 class="text-sm font-medium text-gray-500">Course Utilization</h3>
                  <p class="mt-1 text-2xl font-semibold text-gray-900">{{ statistics.utilizationRate }}%</p>
                </div>
              </div>

              <!-- Course Capacity Chart -->
              <div class="mt-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Course Capacity Overview</h3>
                <div class="h-64 bg-gray-50 rounded-lg p-4">
                  <!-- Chart component will be added here -->
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assignment Modal -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ isEditing ? 'Edit Assignment' : 'New Assignment' }}
          </h3>
          <form @submit.prevent="submitAssignment" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Course</label>
              <select
                v-model="formData.courseId"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Faculty</label>
              <select
                v-model="formData.facultyId"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option v-for="faculty in availableFaculty" :key="faculty.id" :value="faculty.id">
                  {{ faculty.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Course Capacity</label>
              <input
                type="number"
                v-model="formData.capacity"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {{ isEditing ? 'Update' : 'Assign' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Bulk Assignment Modal -->
    <div v-if="showBulkModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div class="relative top-20 mx-auto p-5 border w-3/4 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Bulk Course Assignment</h3>
          <div class="space-y-4">
            <!-- Bulk assignment interface will be implemented here -->
            <div class="flex justify-end space-x-2">
              <button
                @click="closeBulkModal"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                @click="submitBulkAssignment"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { CourseAssignmentService } from '@/services/courseAssignment.service'
import SideNavBar from '@/layouts/SideNavBar.vue'

export default {
  name: 'CourseAssignmentManagement',
  components: {
    SideNavBar
  },
  setup() {
    // State
    const assignments = ref([])
    const courses = ref([])
    const availableFaculty = ref([])
    const statistics = ref({
      totalCourses: 0,
      activeFaculty: 0,
      totalStudents: 0,
      utilizationRate: 0
    })
    const showAssignModal = ref(false)
    const showBulkModal = ref(false)
    const isEditing = ref(false)
    const formData = ref({
      courseId: '',
      facultyId: '',
      capacity: 0
    })

    // Methods
    const fetchAssignments = async () => {
      try {
        const response = await CourseAssignmentService.getFacultyAssignments()
        assignments.value = response.data
      } catch (error) {
        console.error('Error fetching assignments:', error)
      }
    }

    const fetchCourses = async () => {
      try {
        const response = await CourseAssignmentService.getCourses()
        courses.value = response.data
      } catch (error) {
        console.error('Error fetching courses:', error)
      }
    }

    const fetchAvailableFaculty = async () => {
      try {
        const response = await CourseAssignmentService.getAvailableFaculty()
        availableFaculty.value = response.data
      } catch (error) {
        console.error('Error fetching faculty:', error)
      }
    }

    const openAssignModal = () => {
      isEditing.value = false
      formData.value = {
        courseId: '',
        facultyId: '',
        capacity: 0
      }
      showAssignModal.value = true
    }

    const openEditModal = (assignment) => {
      isEditing.value = true
      formData.value = {
        courseId: assignment.courseId,
        facultyId: assignment.facultyId,
        capacity: assignment.capacity
      }
      showAssignModal.value = true
    }

    const closeModal = () => {
      showAssignModal.value = false
      formData.value = {
        courseId: '',
        facultyId: '',
        capacity: 0
      }
    }

    const submitAssignment = async () => {
      try {
        if (isEditing.value) {
          // Update existing assignment
          await CourseAssignmentService.updateCourseCapacity(
            formData.value.courseId,
            formData.value.capacity
          )
        } else {
          // Create new assignment
          await CourseAssignmentService.assignFaculty(formData.value)
        }
        await fetchAssignments()
        closeModal()
      } catch (error) {
        console.error('Error submitting assignment:', error)
      }
    }

    const confirmRemoveAssignment = async (assignment) => {
      if (confirm('Are you sure you want to remove this assignment?')) {
        try {
          await CourseAssignmentService.removeFacultyAssignment(assignment.id)
          await fetchAssignments()
        } catch (error) {
          console.error('Error removing assignment:', error)
        }
      }
    }

    const openBulkAssignModal = () => {
      showBulkModal.value = true
    }

    const closeBulkModal = () => {
      showBulkModal.value = false
    }

    const submitBulkAssignment = async () => {
      // Implement bulk assignment logic
      closeBulkModal()
    }

    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([
        fetchAssignments(),
        fetchCourses(),
        fetchAvailableFaculty()
      ])
    })

    return {
      assignments,
      courses,
      availableFaculty,
      statistics,
      showAssignModal,
      showBulkModal,
      isEditing,
      formData,
      openAssignModal,
      openEditModal,
      closeModal,
      submitAssignment,
      confirmRemoveAssignment,
      openBulkAssignModal,
      closeBulkModal,
      submitBulkAssignment
    }
  }
}
</script> 