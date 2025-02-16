<template>
  <div class="flex">
    <SideNavBar />
    <div class="flex-1">
      <BaseNotificationsView
        ref="baseNotifications"
        :courses="allCourses"
        :is-admin="true"
        description="Send system-wide notifications or course-specific announcements"
        @notification="handleSupportNotification"
      />
    </div>
  </div>
</template>

<script>
import BaseNotificationsView from '@/views/base/BaseNotificationsView.vue'
import useAuthStore from '@/stores/useAuthStore'
import SideNavBar from '@/layouts/SideNavBar.vue'

export default {
  name: 'SupportNotificationsView',
  components: {
    BaseNotificationsView,
    SideNavBar
  },
  data() {
    return {
      allCourses: [
        { id: 1, title: 'Advanced Algorithms' },
        { id: 2, title: 'Machine Learning Fundamentals' },
        { id: 3, title: 'Data Structures' },
        { id: 4, title: 'Web Development' },
        { id: 5, title: 'Database Systems' },
      ]
    }
  },
  computed: {
    userStore() {
      return useAuthStore()
    }
  },
  methods: {
    handleSupportNotification(notification) {
      // Support staff can send both system-wide and course-specific notifications
      if (!this.$refs.baseNotifications) return

      // Allow both system-wide and course-specific notifications
      if (notification.type === 'system' || notification.type === 'course') {
        // For course notifications, verify the course exists
        if (notification.type === 'course') {
          const courseExists = this.allCourses.some(course => course.id === notification.courseId)
          if (!courseExists) {
            console.warn('Attempted to send notification for non-existent course')
            return
          }
        }
        
        this.$refs.baseNotifications.handleNotification(notification)
      }
    }
  }
}
</script> 