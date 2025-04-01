<template>
  <div class="fixed inset-0 flex items-start justify-end p-4 z-50">
    <div
      class="bg-white rounded-xl shadow-xl w-full max-w-md border border-gray-200 max-h-[90vh] flex flex-col transform transition-all duration-300"
      :class="{ 'translate-x-full': !isOpen }"
    >
      <!-- Header -->
      <div
        class="p-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white rounded-t-xl z-10"
      >
        <div class="flex items-center space-x-3">
          <h2 class="text-lg font-semibold text-gray-900">Notifications</h2>
          <span
            v-if="unreadCount"
            class="px-2 py-0.5 bg-maroon-100 text-maroon-800 text-xs font-medium rounded-full"
          >
            {{ unreadCount }} new
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <button
            v-if="hasUnread"
            @click="markAllAsRead"
            class="text-sm text-maroon-600 hover:text-maroon-700 font-medium"
          >
            Mark all as read
          </button>
          <button
            @click="$emit('close')"
            class="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <span class="material-icons text-gray-500">close</span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="p-3 border-b border-gray-100 bg-gray-50 sticky top-[65px] z-10">
        <div class="flex space-x-2">
          <button
            v-for="filter in filters"
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="px-3 py-1 rounded-full text-sm font-medium transition-colors"
            :class="[
              currentFilter === filter.value
                ? 'bg-maroon-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100',
            ]"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="flex-1 overflow-y-auto">
        <div
          v-if="filteredNotifications.length === 0"
          class="flex flex-col items-center justify-center p-8 text-gray-500"
        >
          <div v-if="!isNotificationLoading">
            <span class="material-icons text-4xl mb-2">notifications_off</span>
            <p class="text-center">No notifications to show</p>
          </div>
          <div v-else>
            <miniLoader class=""> Fetching Notifications... </miniLoader>
          </div>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="notification in filteredNotifications"
            :key="notification.id"
            class="p-4 hover:bg-gray-50 transition-colors relative group"
            :class="{ 'bg-maroon-50/30': !notification.read }"
          >
            <!-- Notification Content -->
            <div class="flex items-start space-x-3">
              <!-- Icon -->
              <div
                class="p-2 rounded-full flex-shrink-0"
                :class="getNotificationTypeClasses(notification.type).bgClass"
              >
                <span
                  class="material-icons text-lg"
                  :class="getNotificationTypeClasses(notification.type).textClass"
                >
                  {{ getNotificationIcon(notification.type) }}
                </span>
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                  <span
                    class="text-xs font-medium px-2 py-0.5 rounded-full"
                    :class="getNotificationTypeClasses(notification.type).badgeClass"
                  >
                    {{ notification.category }}
                  </span>
                  <span class="text-xs text-gray-500">{{
                    formatTimestamp(notification.timestamp)
                  }}</span>
                </div>
                <h4 class="font-medium text-gray-900 mb-1">{{ notification.title }}</h4>
                <p class="text-sm text-gray-600 line-clamp-2">{{ notification.message }}</p>

                <!-- Action Buttons -->
                <div class="flex items-center space-x-4 mt-2">
                  <button
                    v-if="notification.actionUrl"
                    @click="handleAction(notification)"
                    class="text-sm text-maroon-600 hover:text-maroon-700 font-medium inline-flex items-center"
                  >
                    View Details
                    <span class="material-icons text-sm ml-1">arrow_forward</span>
                  </button>
                  <button
                    v-if="!notification.read"
                    @click="markAsRead(notification)"
                    class="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Mark as read
                  </button>
                </div>
              </div>

              <!-- Quick Actions -->
              <div class="opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  @click="removeNotification(notification)"
                  class="p-1 hover:bg-gray-200 rounded-full transition-colors"
                  title="Delete Notification"
                >
                  <span class="material-icons text-gray-400 text-sm">delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMoreNotifications" class="p-3 border-t border-gray-100 text-center">
        <button
          @click="loadMore"
          class="text-sm text-maroon-600 hover:text-maroon-700 font-medium"
          :disabled="isLoading"
        >
          <span v-if="isLoading">
            <span class="material-icons animate-spin inline-block">refresh</span>
            Loading...
          </span>
          <span v-else>Load More</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { formatDistanceToNow } from 'date-fns'
import api from '@/utils/api'
import miniLoader from './common/miniLoader.vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'NotificationPanel',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    miniLoader,
  },
  data() {
    return {
      currentFilter: 'all',
      filters: [
        { label: 'All', value: 'all' },
        { label: 'Unread', value: 'unread' },
        { label: 'Course', value: 'course' },
        { label: 'System', value: 'system' },
      ],
      notifications: [
        // {
        //   id: 1,
        //   type: 'course',
        //   category: 'Assignment',
        //   title: 'New Assignment Posted',
        //   message: 'A new assignment has been posted in Advanced Algorithms course.',
        //   timestamp: new Date('2024-01-25T10:00:00'),
        //   read: false,
        //   actionUrl: '/course/assignment/123',
        // },
      ],
      isLoading: false,
      hasMoreNotifications: false,
      page: 1,
      isNotificationLoading: false,
      isDeleting: false,
    }
  },
  computed: {
    filteredNotifications() {
      return this.notifications.filter((notification) => {
        if (this.currentFilter === 'unread') return !notification.read
        if (this.currentFilter === 'course') return notification.notification_type === 'course'
        if (this.currentFilter === 'system') return notification.notification_type === 'system'
        return true
      })
    },
    unreadCount() {
      return this.notifications.filter((n) => !n.read).length
    },
    hasUnread() {
      return this.unreadCount > 0
    },
  },
  methods: {
    showSuccessToast(msg) {
      const toast = useToast() // Call inside the method
      toast.success(msg, { timeout: 2000 })
    },
    showErrorToast(error, defaultMessage) {
      const toast = useToast()
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    },
    getNotificationTypeClasses(type) {
      const classes = {
        course: {
          bgClass: 'bg-blue-100',
          textClass: 'text-blue-600',
          badgeClass: 'bg-blue-100 text-blue-800',
        },
        system: {
          bgClass: 'bg-purple-100',
          textClass: 'text-purple-600',
          badgeClass: 'bg-purple-100 text-purple-800',
        },
        grade: {
          bgClass: 'bg-green-100',
          textClass: 'text-green-600',
          badgeClass: 'bg-green-100 text-green-800',
        },
      }
      return classes[type] || classes.system
    },
    getNotificationIcon(type) {
      const icons = {
        course: 'school',
        system: 'campaign',
        grade: 'grade',
      }
      return icons[type] || 'notifications'
    },
    formatTimestamp(date) {
      return formatDistanceToNow(new Date(date), { addSuffix: true })
    },
    async markAsRead(notification) {
      // TODO: Implement API call
      // notification_id = notification_id.id
      // notification.read = true
      this.markNotificationAsRead(notification)
      this.$emit('update:unread-count', this.unreadCount)
    },
    async markAllAsRead() {
      // TODO: Implement API call
      // this.notifications.forEach((n) => (n.read = true))
      // this.$emit('update:unread-count', 0)
      this.markAllNotificationsAsRead()
    },
    async removeNotification(notification) {
      // TODO: Implement API call
      console.log('Deleting notification')
      this.isDeleting = true
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      console.log(notification)
      try {
        const type = notification.notification_type
        const id = notification.notification_id
        const response = await api.delete(`/notifications/delete/${type}/${id}`, headers)
        this.notifications = this.notifications.filter(
          (n) => n.notification_id !== notification.notification_id,
        )
        this.$emit('update:unread-count', this.unreadCount)
        this.showSuccessToast('Notification has been deleted')
      } catch (error) {
        this.showErrorToast(error, 'Failed to Delete the Notification')
        throw error
      } finally {
        this.isDeleting = false
      }
    },
    handleAction(notification) {
      if (notification.actionUrl) {
        this.$router.push(notification.actionUrl)
        this.$emit('close')
      }
    },
    async loadMore() {
      this.isLoading = true
      // TODO: Implement API call to load more notifications
      await new Promise((resolve) => setTimeout(resolve, 1000))
      this.page++
      this.hasMoreNotifications = this.page < 3 // For demo purposes
      this.isLoading = false
    },

    //API Call to get notification
    async getNotifications() {
      this.isNotificationLoading = true
      console.log('Fetching notification')
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      try {
        const response = await api.get('/notifications', headers)
        response.data.forEach((notif) => {
          this.notifications.push(notif)
        })
      } catch (error) {
        throw error
      } finally {
        this.isNotificationLoading = false
      }
    },
    async markNotificationAsRead(notification) {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }
      try {
        const type = notification.notification_type
        const id = notification.notification_id
        const response = await api.put(`/notifications/${type}/${id}`, {}, headers)
        notification.read = true
        this.$emit('update:unread-count', this.unreadCount)
        return response.data
      } catch (error) {
        throw error
      }
    },
    async markAllNotificationsAsRead() {
      this.isLoading = true
      const token = localStorage.getItem('token')
      if (!token) throw new Error('No authentication token found')

      const notificationsToUpdate = this.notifications
        .filter((n) => !n.read)
        .map((n) => ({
          id: n.notification_id,
          type: n.notification_type,
        }))

      if (notificationsToUpdate.length === 0) {
        this.isLoading = false
        return
      }

      const headers = {
        headers: {
          Authorization: `Bearer ${token}`, // Add token to Authorization header
        },
      }

      try {
        const payload = {
          notifications: notificationsToUpdate,
        }
        await api.put('/notifications/mark-all', payload, headers)
        this.notifications.forEach((n) => {
          n.read = true
        })
        this.$emit('update:unread-count', 0)
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
  },
  mounted() {
    this.getNotifications()
  },
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Animations */
.translate-x-full {
  transform: translateX(100%);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.loading-overlay {
  @apply fixed inset-auto top-24 left-1/2 -translate-x-1/2 py-5 px-12 rounded-md bg-gray-100 shadow-md;
}
</style>
