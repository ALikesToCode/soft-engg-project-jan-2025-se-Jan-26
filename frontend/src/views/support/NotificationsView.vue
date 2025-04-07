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
  <div v-if="isLoading || isSendingNotif" class="loading-overlay">
    <LoadingSpinner />
  </div>
</template>

<script>
import BaseNotificationsView from '@/views/base/BaseNotificationsView.vue'
import useAuthStore from '@/stores/useAuthStore'
import SideNavBar from '@/layouts/SideNavBar.vue'
import { FacultyNotificationService } from '@/services/facultyNotification.service'
import { useCourseStore } from '@/stores/courseStore'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'SupportNotificationsView',
  components: {
    BaseNotificationsView,
    SideNavBar,
    LoadingSpinner,
  },
  data() {
    return {
      isLoading: false,
      isSendingNotif: false,
      allCourses: [
        // { id: 1, title: 'Advanced Algorithms' },
      ],
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
    async handleSupportNotification(notification) {
      // Support staff can send both system-wide and course-specific notifications
      if (!this.$refs.baseNotifications) return
      this.isSendingNotif = true
      // Allow both system-wide and course-specific notifications
      if (notification.type === 'system' || notification.type === 'course') {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')
        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        // For course notifications, verify the course exists
        if (notification.type === 'course') {
          const courseExists = this.allCourses.some((course) => course.id === notification.courseId)
          if (!courseExists) {
            console.warn('Attempted to send notification for non-existent course')
            return
          }
          //Use the same service to create course notification for support as well
          try {
            const response = await FacultyNotificationService.createNotification(
              notification,
              headers,
            )
            console.log('support notification created => ' + response.data)
            this.showSuccessToast('Notification Sent Successfully')
          } catch (error) {
            this.isSendingNotif = false
            this.showErrorToast(error, 'Failed to Send Notification')
          }
        } else {
          //API call to save system notification for support
          console.log('coming here for support system notif')
          try {
            const response = await FacultyNotificationService.createSystemNotification(
              notification,
              headers,
            )
            console.log('support system notification created => ' + response.data)
            this.showSuccessToast('Notification Sent Successfully')
          } catch (error) {
            this.isSendingNotif = false
            this.showErrorToast(error, 'Failed to Send Notification')
          }
        }
        //API call to save faculty notification
        // this.$refs.baseNotifications.handleNotification(notification)
      }
      this.isSendingNotif = false
    },

    async getSupportCourses() {
      this.isLoading = true;
      try {
        // Clear existing courses first
        this.allCourses = [];
        
        // Use try-catch for the API call to properly handle errors
        const response = await this.courseStore.getUserCourses();
        
        if (response && response.data && response.data.length > 0) {
          this.allCourses = response.data;
          console.log(`Loaded ${this.allCourses.length} courses for support notifications`);
        } else {
          console.log('No courses available in the response');
        }
      } catch (error) {
        console.error('Failed to load courses for support:', error);
        this.showErrorToast(error, 'Failed to load courses');
      } finally {
        this.isLoading = false;
      }
    },
  },
  mounted() {
    this.getSupportCourses()
  },
}
</script>
<style scoped>
.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
