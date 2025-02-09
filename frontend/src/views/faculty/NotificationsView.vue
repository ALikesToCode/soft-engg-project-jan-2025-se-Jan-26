<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-4xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Send Notifications</h1>
        <p class="text-gray-600 mt-1">Send notifications to your students or announce system-wide updates</p>
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
          <div v-for="notification in recentNotifications" 
               :key="notification.id"
               class="bg-white rounded-xl shadow-sm border border-gray-100 p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-3">
                <span 
                  class="text-sm px-2 py-1 rounded-full"
                  :class="{
                    'bg-blue-100 text-blue-800': notification.type === 'course',
                    'bg-purple-100 text-purple-800': notification.type === 'system'
                  }"
                >
                  {{ notification.type === 'course' ? 'Course' : 'System' }}
                </span>
                <span 
                  class="text-sm px-2 py-1 rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': notification.priority === 'low',
                    'bg-yellow-100 text-yellow-800': notification.priority === 'medium',
                    'bg-orange-100 text-orange-800': notification.priority === 'high',
                    'bg-red-100 text-red-800': notification.priority === 'urgent'
                  }"
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

export default {
  name: 'NotificationsView',
  components: {
    NotificationForm
  },
  data() {
    return {
      isAdmin: true, // This should come from your auth system
      courses: [
        { id: 1, title: 'Advanced Algorithms' },
        { id: 2, title: 'Machine Learning Fundamentals' },
        { id: 3, title: 'Data Structures' }
      ],
      recentNotifications: [
        {
          id: 1,
          type: 'course',
          courseId: 1,
          priority: 'high',
          category: 'announcement',
          title: 'Assignment Deadline Extended',
          message: 'The deadline for Assignment 3 has been extended to next Friday.',
          createdAt: new Date('2024-01-20T10:00:00')
        },
        {
          id: 2,
          type: 'system',
          priority: 'urgent',
          category: 'maintenance',
          title: 'Scheduled Maintenance',
          message: 'The system will be under maintenance this Sunday from 2 AM to 4 AM.',
          createdAt: new Date('2024-01-19T15:30:00')
        }
      ]
    }
  },
  methods: {
    async handleNotification(notification) {
      // TODO: Implement API call to send notification
      console.log('Sending notification:', notification);
      
      // For demo purposes, add to recent notifications
      this.recentNotifications.unshift({
        id: Date.now(),
        ...notification,
        createdAt: new Date()
      });
    },
    formatDate(date) {
      const d = new Date(date);
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const month = months[d.getMonth()];
      const day = d.getDate();
      const year = d.getFullYear();
      const hours = d.getHours();
      const minutes = d.getMinutes().toString().padStart(2, '0');
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const formattedHours = hours % 12 || 12;
      
      return `${month} ${day}, ${year} ${formattedHours}:${minutes} ${ampm}`;
    },
    getCourseTitle(courseId) {
      const course = this.courses.find(c => c.id === courseId)
      return course ? course.title : 'Unknown Course'
    }
  }
}
</script> 