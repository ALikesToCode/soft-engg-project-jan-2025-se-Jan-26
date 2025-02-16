<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-4xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Send Notifications</h1>
        <p class="text-gray-600 mt-1">
          {{ description }}
        </p>
      </div>

      <NotificationForm
        :courses="courses"
        :is-admin="isAdmin"
        @send-notification="handleNotification"
      />

      <!-- Recent Notifications -->
      <div class="mt-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-4">Recent Notifications</h2>
        <div class="space-y-4">
          <div
            v-for="notification in recentNotifications"
            :key="notification.id"
            class="bg-white rounded-xl shadow-sm border border-gray-100 p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-3">
                <span
                  class="text-sm px-2 py-1 rounded-full"
                  :class="getTypeClass(notification.type)"
                >
                  {{ notification.type === 'course' ? 'Course' : 'System' }}
                </span>
                <span
                  class="text-sm px-2 py-1 rounded-full"
                  :class="getPriorityClass(notification.priority)"
                >
                  {{ notification.priority }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ notification.category }}
                </span>
              </div>
              <span class="text-sm text-gray-500">
                {{ formatDate(notification.createdAt) }}
              </span>
            </div>
            <h3 class="font-semibold text-gray-800">{{ notification.title }}</h3>
            <p class="text-gray-600 text-sm mt-1">{{ notification.message }}</p>
            <div v-if="notification.type === 'course'" class="mt-2 text-sm text-gray-500">
              Course: {{ getCourseTitle(notification.courseId) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NotificationForm from '@/components/NotificationForm.vue'
import formatDateFunc from '@/utils/formatDate'

export default {
  name: 'BaseNotificationsView',
  components: {
    NotificationForm
  },
  props: {
    courses: {
      type: Array,
      required: true
    },
    isAdmin: {
      type: Boolean,
      default: false
    },
    description: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      recentNotifications: [
        {
          id: 1,
          type: 'system',
          priority: 'urgent',
          category: 'maintenance',
          title: 'Scheduled Maintenance',
          message: 'The system will be under maintenance this Sunday from 2 AM to 4 AM.',
          createdAt: new Date('2024-01-20T10:00:00'),
        },
        {
          id: 2,
          type: 'course',
          courseId: 1,
          priority: 'high',
          category: 'announcement',
          title: 'Course Update',
          message: 'Important updates have been made to the course materials.',
          createdAt: new Date('2024-01-19T15:30:00'),
        }
      ]
    }
  },
  methods: {
    handleNotification(notification) {
      // Validate notification type based on admin status
      if (!this.isAdmin && notification.type === 'system') {
        console.warn('Non-admin user attempted to send system notification')
        return
      }

      // For course notifications, verify the course exists
      if (notification.type === 'course') {
        const courseExists = this.courses.some(course => course.id === notification.courseId)
        if (!courseExists) {
          console.warn('Attempted to send notification for non-existent course')
          return
        }
      }

      // Emit the notification to parent component for processing
      this.$emit('notification', notification)

      // For demo purposes, add to recent notifications
      this.recentNotifications.unshift({
        id: Date.now(),
        ...notification,
        createdAt: new Date(),
      })
    },
    formatDate(date) {
      return formatDateFunc(date)
    },
    getCourseTitle(courseId) {
      const course = this.courses.find((c) => c.id === courseId)
      return course ? course.title : 'Unknown Course'
    },
    getTypeClass(type) {
      return {
        'bg-blue-100 text-blue-800': type === 'course',
        'bg-purple-100 text-purple-800': type === 'system',
      }
    },
    getPriorityClass(priority) {
      return {
        'bg-green-100 text-green-800': priority === 'low',
        'bg-yellow-100 text-yellow-800': priority === 'medium',
        'bg-orange-100 text-orange-800': priority === 'high',
        'bg-red-100 text-red-800': priority === 'urgent',
      }
    }
  }
}
</script> 