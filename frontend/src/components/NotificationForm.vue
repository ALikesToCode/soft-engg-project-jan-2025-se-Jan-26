<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-800">Send Notification</h2>
      <div class="flex items-center space-x-2">
        <span 
          class="text-sm px-3 py-1 rounded-full"
          :class="{
            'bg-blue-100 text-blue-800': notificationType === 'course',
            'bg-purple-100 text-purple-800': notificationType === 'system'
          }"
        >
          {{ notificationType === 'course' ? 'Course Notification' : 'System Notification' }}
        </span>
      </div>
    </div>

    <!-- Notification Type Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Notification Type</label>
      <div class="flex space-x-4">
        <label class="flex items-center">
          <input 
            type="radio" 
            v-model="notificationType" 
            value="course"
            class="form-radio text-maroon-600"
          >
          <span class="ml-2 text-gray-700">Course Specific</span>
        </label>
        <label class="flex items-center">
          <input 
            type="radio" 
            v-model="notificationType" 
            value="system"
            class="form-radio text-maroon-600"
            :disabled="!isAdmin"
          >
          <span class="ml-2 text-gray-700">System Wide</span>
        </label>
      </div>
    </div>

    <!-- Course Selection (for course notifications) -->
    <div v-if="notificationType === 'course'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Select Course</label>
      <select 
        v-model="selectedCourse"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
      >
        <option value="">Select a course</option>
        <option v-for="course in courses" :key="course.id" :value="course.id">
          {{ course.title }}
        </option>
      </select>
    </div>

    <!-- Priority Level -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Priority Level</label>
      <select 
        v-model="priority"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="urgent">Urgent</option>
      </select>
    </div>

    <!-- Category -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
      <select 
        v-model="category"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
      >
        <option value="announcement">Announcement</option>
        <option value="update">Update</option>
        <option value="reminder">Reminder</option>
        <option value="alert">Alert</option>
        <option v-if="notificationType === 'system'" value="maintenance">System Maintenance</option>
        <option v-if="notificationType === 'system'" value="technical">Technical Issue</option>
      </select>
    </div>

    <!-- Title -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
      <input 
        type="text"
        v-model="title"
        placeholder="Enter notification title"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
      >
    </div>

    <!-- Message -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Message</label>
      <textarea 
        v-model="message"
        rows="4"
        placeholder="Enter your message"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
      ></textarea>
    </div>

    <!-- Schedule Options -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Schedule</label>
      <div class="flex items-center space-x-4">
        <label class="flex items-center">
          <input 
            type="radio" 
            v-model="scheduleType" 
            value="now"
            class="form-radio text-maroon-600"
          >
          <span class="ml-2 text-gray-700">Send Now</span>
        </label>
        <label class="flex items-center">
          <input 
            type="radio" 
            v-model="scheduleType" 
            value="schedule"
            class="form-radio text-maroon-600"
          >
          <span class="ml-2 text-gray-700">Schedule</span>
        </label>
      </div>
    </div>

    <!-- Schedule DateTime (if scheduled) -->
    <div v-if="scheduleType === 'schedule'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Schedule Date & Time</label>
      <input 
        type="datetime-local"
        v-model="scheduledDateTime"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500"
      >
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-end space-x-4">
      <button 
        @click="resetForm"
        class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        Reset
      </button>
      <button 
        @click="sendNotification"
        class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
        :disabled="!isFormValid"
      >
        {{ scheduleType === 'schedule' ? 'Schedule' : 'Send' }} Notification
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationForm',
  props: {
    isAdmin: {
      type: Boolean,
      default: false
    },
    courses: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      notificationType: 'course',
      selectedCourse: '',
      priority: 'medium',
      category: 'announcement',
      title: '',
      message: '',
      scheduleType: 'now',
      scheduledDateTime: null
    }
  },
  computed: {
    isFormValid() {
      const baseValidation = this.title.trim() && this.message.trim() && 
                            this.priority && this.category;
      
      if (this.notificationType === 'course') {
        return baseValidation && this.selectedCourse;
      }
      
      if (this.scheduleType === 'schedule') {
        return baseValidation && this.scheduledDateTime;
      }
      
      return baseValidation;
    }
  },
  methods: {
    async sendNotification() {
      try {
        const notification = {
          type: this.notificationType,
          courseId: this.selectedCourse,
          priority: this.priority,
          category: this.category,
          title: this.title,
          message: this.message,
          scheduleType: this.scheduleType,
          scheduledDateTime: this.scheduledDateTime
        };

        // TODO: Implement API call
        await this.$emit('send-notification', notification);
        this.$toast.success(`Notification ${this.scheduleType === 'schedule' ? 'scheduled' : 'sent'} successfully`);
        this.resetForm();
      } catch (error) {
        this.$toast.error('Failed to send notification');
      }
    },
    resetForm() {
      this.notificationType = 'course';
      this.selectedCourse = '';
      this.priority = 'medium';
      this.category = 'announcement';
      this.title = '';
      this.message = '';
      this.scheduleType = 'now';
      this.scheduledDateTime = null;
    }
  }
}
</script>

<style scoped>
.form-radio {
  @apply h-4 w-4 text-maroon-600 border-gray-300 focus:ring-maroon-500;
}
</style> 