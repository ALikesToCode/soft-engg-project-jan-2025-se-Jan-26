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
  <div v-if="isLoading || isSendingNotif" class="loading-overlay">
    <LoadingSpinner />
  </div>
</template>

<script>
import BaseNotificationsView from '@/views/base/BaseNotificationsView.vue'
import useAuthStore from '@/stores/useAuthStore'
import SideNavBar from '@/layouts/SideNavBar.vue'
import { useCourseStore } from '@/stores/courseStore'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { FacultyNotificationService } from '@/services/facultyNotification.service'
import { useToast } from 'vue-toastification'

export default {
  name: 'FacultyNotificationsView',
  components: {
    BaseNotificationsView,
    SideNavBar,
    LoadingSpinner,
  },
  data() {
    return {
      enrolledCourses: [],
      isLoading: false,
      isSendingNotif: false,
    }
  },
  computed: {
    userStore() {
      return useAuthStore()
    },
    courseStore() {
      return useCourseStore()
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
    async handleFacultyNotification(notification) {
      // Faculty can only send course-specific notifications
      if (!this.$refs.baseNotifications) return
      this.isSendingNotif = true
      if (notification.type === 'course') {
        // Verify the course is one they're enrolled in
        const isEnrolled = this.enrolledCourses.some(
          (course) => course.id === notification.courseId,
        )
        if (isEnrolled) {
          const token = localStorage.getItem('token')
          if (!token) throw new Error('No authentication token found')

          const headers = {
            headers: {
              Authorization: `Bearer ${token}`, // Add token to Authorization header
            },
          }
          //API call to save faculty notification
          try {
            const response = await FacultyNotificationService.createNotification(
              notification,
              headers,
            )
            console.log('here ' + response.data)
            if (!response || response.status !== 200) {
              throw new Error('Unexpected response format')
            }
            this.isSendingNotif = false
            this.showSuccessToast('Notification sent successfully')
          } catch (error) {
            this.isSendingNotif = false
            this.showErrorToast(error, 'Failed to send the notification')
          }
        } else {
          console.warn('Faculty attempted to send notification for non-enrolled course')
        }
      } else {
        console.warn('Faculty attempted to send system notification')
      }
      this.isSendingNotif = false
    },
    async getFacultyCourses() {
      this.isLoading = true
      try {
        const response = await this.courseStore.getFacultyCourses()
        if (response && response.data) {
          this.enrolledCourses = response.data
          console.log(`Loaded ${this.enrolledCourses.length} courses for faculty notifications`)
        } else {
          console.log('No courses available in the response')
        }
      } catch (error) {
        this.showErrorToast(error, 'Failed to load the courses')
        console.error('Error loading faculty courses:', error)
      } finally {
        this.isLoading = false
      }
    },
  },
  mounted() {
    this.getFacultyCourses()
  },
}
</script>
<style scoped>
.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
