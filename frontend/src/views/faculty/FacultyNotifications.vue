<!-- Faculty Notifications Component -->
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
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Notifications</h1>
              <p class="mt-2 text-gray-600">Manage and send course-specific notifications</p>
            </div>
            <button
              @click="openCreateModal"
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Create Notification
            </button>
          </div>
        </header>

        <!-- Notification Filters -->
        <div class="bg-white rounded-lg shadow-md p-4 mb-6">
          <div class="flex items-center space-x-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700">Course</label>
              <select
                v-model="filters.courseId"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">All Courses</option>
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.name }}
                </option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700">Type</label>
              <select
                v-model="filters.type"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">All Types</option>
                <option value="announcement">Announcement</option>
                <option value="reminder">Reminder</option>
                <option value="alert">Alert</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <select
                v-model="filters.status"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="scheduled">Scheduled</option>
                <option value="expired">Expired</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Notifications List -->
        <div class="space-y-4">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="bg-white rounded-lg shadow-md p-6"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      {
                        'bg-blue-100 text-blue-800': notification.type === 'announcement',
                        'bg-yellow-100 text-yellow-800': notification.type === 'reminder',
                        'bg-red-100 text-red-800': notification.type === 'alert'
                      }
                    ]"
                  >
                    {{ notification.type }}
                  </span>
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      {
                        'bg-green-100 text-green-800': notification.status === 'active',
                        'bg-purple-100 text-purple-800': notification.status === 'scheduled',
                        'bg-gray-100 text-gray-800': notification.status === 'expired'
                      }
                    ]"
                  >
                    {{ notification.status }}
                  </span>
                </div>
                <h3 class="mt-2 text-lg font-medium text-gray-900">{{ notification.title }}</h3>
                <p class="mt-1 text-gray-600">{{ notification.message }}</p>
                <div class="mt-2 text-sm text-gray-500">
                  <span>{{ notification.courseName }}</span>
                  <span class="mx-2">•</span>
                  <span>{{ formatDate(notification.timestamp) }}</span>
                  <span v-if="notification.scheduledFor" class="mx-2">•</span>
                  <span v-if="notification.scheduledFor">Scheduled for: {{ formatDate(notification.scheduledFor) }}</span>
                </div>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="editNotification(notification)"
                  class="text-indigo-600 hover:text-indigo-900"
                >
                  Edit
                </button>
                <button
                  @click="deleteNotification(notification)"
                  class="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Notification Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div class="relative top-20 mx-auto p-5 border w-2/3 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ isEditing ? 'Edit Notification' : 'Create Notification' }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <form @submit.prevent="submitNotification" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Course</label>
              <select
                v-model="formData.courseId"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              >
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Type</label>
              <select
                v-model="formData.type"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              >
                <option value="announcement">Announcement</option>
                <option value="reminder">Reminder</option>
                <option value="alert">Alert</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Title</label>
              <input
                type="text"
                v-model="formData.title"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Message</label>
              <textarea
                v-model="formData.message"
                rows="4"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Schedule (Optional)</label>
              <input
                type="datetime-local"
                v-model="formData.scheduledFor"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                {{ isEditing ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { FacultyNotificationService } from '@/services/facultyNotification.service'
import SideNavBar from '@/layouts/SideNavBar.vue'

export default {
  name: 'FacultyNotifications',
  components: {
    SideNavBar
  },
  setup() {
    // State
    const notifications = ref([])
    const courses = ref([])
    const filters = ref({
      courseId: '',
      type: '',
      status: ''
    })
    const showModal = ref(false)
    const isEditing = ref(false)
    const formData = ref({
      courseId: '',
      type: 'announcement',
      title: '',
      message: '',
      scheduledFor: ''
    })

    // Methods
    const fetchNotifications = async () => {
      try {
        const response = await FacultyNotificationService.getNotifications(filters.value)
        notifications.value = response.data
      } catch (error) {
        console.error('Error fetching notifications:', error)
      }
    }

    const fetchCourses = async () => {
      try {
        const response = await FacultyNotificationService.getCourses()
        courses.value = response.data
      } catch (error) {
        console.error('Error fetching courses:', error)
      }
    }

    const openCreateModal = () => {
      isEditing.value = false
      formData.value = {
        courseId: '',
        type: 'announcement',
        title: '',
        message: '',
        scheduledFor: ''
      }
      showModal.value = true
    }

    const editNotification = (notification) => {
      isEditing.value = true
      formData.value = { ...notification }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      formData.value = {
        courseId: '',
        type: 'announcement',
        title: '',
        message: '',
        scheduledFor: ''
      }
    }

    const submitNotification = async () => {
      try {
        if (isEditing.value) {
          await FacultyNotificationService.updateNotification(formData.value.id, formData.value)
        } else {
          await FacultyNotificationService.createNotification(formData.value)
        }
        await fetchNotifications()
        closeModal()
      } catch (error) {
        console.error('Error submitting notification:', error)
      }
    }

    const deleteNotification = async (notification) => {
      if (confirm('Are you sure you want to delete this notification?')) {
        try {
          await FacultyNotificationService.deleteNotification(notification.id)
          await fetchNotifications()
        } catch (error) {
          console.error('Error deleting notification:', error)
        }
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString()
    }

    // Watch for filter changes
    watch(filters, () => {
      fetchNotifications()
    })

    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([
        fetchNotifications(),
        fetchCourses()
      ])
    })

    return {
      notifications,
      courses,
      filters,
      showModal,
      isEditing,
      formData,
      openCreateModal,
      editNotification,
      closeModal,
      submitNotification,
      deleteNotification,
      formatDate
    }
  }
}
</script> 