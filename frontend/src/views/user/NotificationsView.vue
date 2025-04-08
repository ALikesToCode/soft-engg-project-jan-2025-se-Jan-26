<template>
  <div class="flex">
    <SideNavBar />
    <div class="flex-1">
      <div class="min-h-screen bg-gray-50 p-6">
        <div class="max-w-4xl mx-auto">
          <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-800">Your Notifications</h1>
            <p class="text-gray-600 mt-1">
              Stay updated with course announcements and system notifications
            </p>
          </div>

          <!-- Notification Filters -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
            <div class="flex flex-wrap items-center gap-4">
              <div>
                <label class="text-sm font-medium text-gray-700 mb-1 block">Filter By</label>
                <div class="flex space-x-2">
                  <button
                    v-for="filter in filters"
                    :key="filter.value"
                    @click="activeFilter = filter.value"
                    class="px-3 py-1 rounded-full text-sm border transition-colors"
                    :class="activeFilter === filter.value ? 'bg-maroon-50 text-maroon-700 border-maroon-300' : 'text-gray-600 border-gray-200 hover:bg-gray-50'"
                  >
                    {{ filter.label }}
                  </button>
                </div>
              </div>
              
              <div class="ml-auto">
                <button
                  @click="markAllAsRead"
                  class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-lg text-sm transition-colors flex items-center"
                  :disabled="isLoading || filteredNotifications.filter(n => !n.read).length === 0"
                >
                  <span class="material-icons text-sm mr-1">done_all</span>
                  Mark All as Read
                </button>
              </div>
            </div>
          </div>

          <!-- Notifications List -->
          <div v-if="isLoading" class="flex justify-center py-12">
            <LoadingSpinner />
          </div>
          
          <div v-else-if="filteredNotifications.length === 0" class="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <div class="text-gray-400 mb-4">
              <span class="material-icons text-6xl">notifications_none</span>
            </div>
            <h2 class="text-xl font-semibold text-gray-700 mb-2">No notifications found</h2>
            <p class="text-gray-500 max-w-md mx-auto">
              {{ getEmptyStateMessage() }}
            </p>
          </div>
          
          <div v-else class="space-y-4">
            <div
              v-for="notification in filteredNotifications"
              :key="`${notification.notification_type}-${notification.notification_id}`"
              class="bg-white rounded-xl shadow-sm border transition-all"
              :class="notification.read ? 'border-gray-100' : 'border-maroon-200 shadow-md'"
            >
              <div class="p-4">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center space-x-2">
                    <span
                      class="text-sm px-2 py-1 rounded-full"
                      :class="getTypeClass(notification.notification_type)"
                    >
                      {{ notification.notification_type === 'course' ? 'Course' : 'System' }}
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
                  <div class="flex items-center space-x-3">
                    <span class="text-sm text-gray-500">
                      {{ formatDate(notification.timestamp) }}
                    </span>
                    <div class="flex space-x-1">
                      <button
                        v-if="!notification.read"
                        @click="markAsRead(notification)"
                        class="p-1 text-gray-500 hover:text-maroon-600 rounded-full hover:bg-gray-100"
                        title="Mark as read"
                      >
                        <span class="material-icons text-base">done</span>
                      </button>
                      <button
                        @click="deleteNotification(notification)"
                        class="p-1 text-gray-500 hover:text-red-600 rounded-full hover:bg-gray-100"
                        title="Delete notification"
                      >
                        <span class="material-icons text-base">delete</span>
                      </button>
                    </div>
                  </div>
                </div>
                <h3 class="font-semibold text-gray-800">{{ notification.title }}</h3>
                <p class="text-gray-600 text-sm mt-1">{{ notification.message }}</p>
                <div v-if="notification.notification_type === 'course'" class="mt-2 text-sm text-gray-500">
                  Course: {{ getCourseTitle(notification.course_id) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '@/layouts/SideNavBar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import formatDateFunc from '@/utils/formatDate'
import { FacultyNotificationService } from '@/services/facultyNotification.service'
import { useCourseStore } from '@/stores/courseStore'
import { useToast } from 'vue-toastification'
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'UserNotificationsView',
  components: {
    SideNavBar,
    LoadingSpinner,
  },
  setup() {
    const toast = useToast()
    const isLoading = ref(false)
    const notifications = ref([])
    const activeFilter = ref('all')
    const courses = ref([])
    const courseStore = useCourseStore()
    
    const filters = [
      { label: 'All', value: 'all' },
      { label: 'Unread', value: 'unread' },
      { label: 'Course', value: 'course' },
      { label: 'System', value: 'system' },
      { label: 'Urgent', value: 'urgent' },
    ]
    
    const filteredNotifications = computed(() => {
      if (activeFilter.value === 'all') {
        return notifications.value
      } else if (activeFilter.value === 'unread') {
        return notifications.value.filter(n => !n.read)
      } else if (activeFilter.value === 'course') {
        return notifications.value.filter(n => n.notification_type === 'course')
      } else if (activeFilter.value === 'system') {
        return notifications.value.filter(n => n.notification_type === 'system')
      } else if (activeFilter.value === 'urgent') {
        return notifications.value.filter(n => n.priority === 'urgent')
      }
      return notifications.value
    })
    
    const loadNotifications = async () => {
      isLoading.value = true
      try {
        const response = await FacultyNotificationService.getRecentNotifications()
        notifications.value = response.data
          .map((notification) => {
            const isRead = notifications.value.some(n => n.notification_id === notification.notification_id && n.read)
            return {
              ...notification,
              read: isRead,
            }
          })
          .sort((a, b) => {
            if (a.read !== b.read) {
              return a.read ? 1 : -1
            }
            return new Date(b.timestamp) - new Date(a.timestamp)
          })

        console.log('Loaded notifications:', notifications.value)
      } catch (error) {
        console.error('Failed to load notifications:', error)
        toast.error('Failed to load notifications')
      } finally {
        isLoading.value = false
      }
    }
    
    const loadCourses = async () => {
      try {
        const response = await courseStore.getUserCourses();
        if (response && response.data) {
          courses.value = response.data;
          console.log(`Loaded ${courses.value.length} courses for user notifications`);
        } else {
          console.log('No courses available in the response');
        }
      } catch (error) {
        console.error('Failed to load courses:', error);
        toast.error('Failed to load courses');
      }
    }
    
    const markAsRead = async (notification) => {
      try {
        await FacultyNotificationService.markAsRead(notification.notification_id, notification.type)
        
        // Update local state
        notification.read = true
        if (!notifications.value.some(n => n.notification_id === notification.notification_id && n.read)) {
          notifications.value.push({ ...notification, read: true })
        }
        
        toast.success('Notification marked as read')
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
        toast.error('Failed to update notification')
      }
    }
    
    const markAllAsRead = async () => {
      try {
        const unreadNotifications = notifications.value
          .filter(n => !n.read)
          .map(n => ({ 
            id: n.notification_id, 
            type: n.notification_type 
          }))
          
        if (unreadNotifications.length === 0) return
        
        await FacultyNotificationService.markAllAsRead(unreadNotifications)
        
        // Update local state
        notifications.value.forEach(n => {
          n.read = true
        })
        
        toast.success('All notifications marked as read')
      } catch (error) {
        console.error('Failed to mark all notifications as read:', error)
        toast.error('Failed to update notifications')
      }
    }
    
    const deleteNotification = async (notification) => {
      try {
        await FacultyNotificationService.deleteNotification(
          notification.notification_id,
          notification.notification_type
        )
        
        // Update local state
        notifications.value = notifications.value.filter(
          n => n.notification_id !== notification.notification_id
        )
        
        toast.success('Notification deleted')
      } catch (error) {
        console.error('Failed to delete notification:', error)
        toast.error('Failed to delete notification')
      }
    }
    
    const formatDate = (date) => {
      return formatDateFunc(date)
    }
    
    const getCourseTitle = (courseId) => {
      const course = courses.value.find(c => c.id === courseId)
      return course ? course.title : 'Unknown Course'
    }
    
    const getTypeClass = (type) => {
      return {
        'bg-blue-100 text-blue-800': type === 'course',
        'bg-purple-100 text-purple-800': type === 'system',
      }
    }
    
    const getPriorityClass = (priority) => {
      return {
        'bg-green-100 text-green-800': priority === 'low',
        'bg-yellow-100 text-yellow-800': priority === 'medium',
        'bg-orange-100 text-orange-800': priority === 'high',
        'bg-red-100 text-red-800': priority === 'urgent',
      }
    }
    
    const getEmptyStateMessage = () => {
      if (activeFilter.value === 'unread') {
        return 'You have no unread notifications. Check back later for updates.'
      } else if (activeFilter.value === 'course') {
        return 'No course notifications found. Your instructors will post updates here.'
      } else if (activeFilter.value === 'system') {
        return 'No system notifications found. Important platform announcements will appear here.'
      } else if (activeFilter.value === 'urgent') {
        return 'No urgent notifications. Critical updates will be highlighted here.'
      }
      return 'You have no notifications yet. Check back later for updates.'
    }
    
    onMounted(() => {
      loadNotifications()
      loadCourses()
    })
    
    return {
      isLoading,
      notifications,
      activeFilter,
      filters,
      filteredNotifications,
      courses,
      
      markAsRead,
      markAllAsRead,
      deleteNotification,
      formatDate,
      getCourseTitle,
      getTypeClass,
      getPriorityClass,
      getEmptyStateMessage
    }
  }
}
</script>

<style scoped>
.material-icons {
  font-size: inherit;
  line-height: inherit;
  vertical-align: middle;
}
</style>