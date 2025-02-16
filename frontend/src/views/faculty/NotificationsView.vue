<template>
  <div class="flex">
    <SideNavBar />
    <div class="flex-1">
      <BaseNotificationsView
        ref="baseNotifications"
        :courses="enrolledCourses"
        :is-admin="false"
        description="Send notifications to your enrolled courses"
        @notification="handleFacultyNotification"
      />
    </div>
  </div>
</template>

<script>
import BaseNotificationsView from '@/views/base/BaseNotificationsView.vue'
import useAuthStore from '@/stores/useAuthStore'
import SideNavBar from '@/layouts/SideNavBar.vue'

export default {
  name: 'FacultyNotificationsView',
  components: {
    BaseNotificationsView,
    SideNavBar
  },
  data() {
    return {
      enrolledCourses: [
        // This would typically come from an API based on the faculty's enrollment
        { id: 1, title: 'Advanced Algorithms' },
        { id: 2, title: 'Machine Learning Fundamentals' }
      ]
    }
  },
  computed: {
    userStore() {
      return useAuthStore()
    }
  },
  methods: {
    handleFacultyNotification(notification) {
      // Faculty can only send course-specific notifications
      if (!this.$refs.baseNotifications) return

      if (notification.type === 'course') {
        // Verify the course is one they're enrolled in
        const isEnrolled = this.enrolledCourses.some(course => course.id === notification.courseId)
        if (isEnrolled) {
          this.$refs.baseNotifications.handleNotification(notification)
        } else {
          console.warn('Faculty attempted to send notification for non-enrolled course')
        }
      } else {
        console.warn('Faculty attempted to send system notification')
      }
    }
  }
}
</script>
