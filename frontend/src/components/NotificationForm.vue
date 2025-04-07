<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100">
    <!-- Form Header -->
    <div class="p-6 border-b border-gray-100">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">Send Notification</h2>
          <p class="text-gray-600 mt-1">Communicate important updates to your students</p>
        </div>
        <span
          class="px-3 py-1 rounded-full text-sm font-medium flex items-center"
          :class="{
            'bg-blue-100 text-blue-800': notificationType === 'course',
            'bg-purple-100 text-purple-800': notificationType === 'system',
          }"
        >
          <span class="material-icons text-sm mr-1">
            {{ notificationType === 'course' ? 'school' : 'campaign' }}
          </span>
          {{ notificationType === 'course' ? 'Course Notification' : 'System Notification' }}
        </span>
      </div>
    </div>

    <!-- Form Content -->
    <div class="p-6 space-y-6">
      <!-- Notification Type Selection -->
      <div class="grid grid-cols-2 gap-4">
        <button
          @click="notificationType = 'course'"
          class="p-4 rounded-lg border-2 transition-all duration-200 flex items-center"
          :class="[
            notificationType === 'course'
              ? 'border-maroon-600 bg-maroon-50'
              : 'border-gray-200 hover:border-gray-300',
          ]"
        >
          <span
            class="p-2 rounded-lg mr-3"
            :class="notificationType === 'course' ? 'bg-maroon-100' : 'bg-gray-100'"
          >
            <span
              class="material-icons"
              :class="notificationType === 'course' ? 'text-maroon-600' : 'text-gray-500'"
              >school</span
            >
          </span>
          <div class="text-left">
            <div class="font-medium text-gray-900">Course Specific</div>
            <div class="text-sm text-gray-600">Send to students in a specific course</div>
          </div>
        </button>

        <button
          v-if="showSystemOption"
          @click="notificationType = 'system'"
          class="p-4 rounded-lg border-2 transition-all duration-200 flex items-center"
          :class="[
            notificationType === 'system'
              ? 'border-maroon-600 bg-maroon-50'
              : 'border-gray-200 hover:border-gray-300',
          ]"
        >
          <span
            class="p-2 rounded-lg mr-3"
            :class="notificationType === 'system' ? 'bg-maroon-100' : 'bg-gray-100'"
          >
            <span
              class="material-icons"
              :class="notificationType === 'system' ? 'text-maroon-600' : 'text-gray-500'"
              >campaign</span
            >
          </span>
          <div class="text-left">
            <div class="font-medium text-gray-900">System Wide</div>
            <div class="text-sm text-gray-600">Send to all platform users</div>
          </div>
        </button>
      </div>

      <!-- Course Selection -->
      <div v-if="notificationType === 'course'" class="space-y-2">
        <label class="block text-sm font-medium text-gray-900">Select Course</label>
        <div class="relative">
          <select
            v-model="selectedCourse"
            class="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 appearance-none"
          >
            <option value="">Select a course</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.title }}
            </option>
          </select>
          <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <span class="material-icons text-gray-400">expand_more</span>
          </span>
        </div>
      </div>

      <!-- Priority & Category -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Priority -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-900">Priority Level</label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="level in priorityLevels"
              :key="level.value"
              @click="priority = level.value"
              class="p-2 rounded-lg border text-center transition-all duration-200"
              :class="[
                priority === level.value
                  ? `${level.activeClasses} border-${level.color}-600`
                  : 'border-gray-200 hover:border-gray-300',
              ]"
            >
              <span
                class="material-icons text-sm mb-1"
                :class="priority === level.value ? `text-${level.color}-600` : 'text-gray-400'"
                >{{ level.icon }}</span
              >
              <div
                class="text-xs font-medium"
                :class="priority === level.value ? `text-${level.color}-600` : 'text-gray-600'"
              >
                {{ level.label }}
              </div>
            </button>
          </div>
        </div>

        <!-- Category -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-900">Category</label>
          <div class="relative">
            <select
              v-model="category"
              class="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 appearance-none"
            >
              <option v-for="cat in availableCategories" :key="cat.value" :value="cat.value">
                {{ cat.label }}
              </option>
            </select>
            <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span class="material-icons text-gray-400">expand_more</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Title -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-900">Title</label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span class="material-icons text-gray-400">title</span>
          </span>
          <input
            type="text"
            v-model="title"
            placeholder="Enter notification title"
            class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 placeholder-gray-500"
          />
        </div>
      </div>

      <!-- Message -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-900">Message</label>
        <div class="relative">
          <textarea
            v-model="message"
            rows="4"
            placeholder="Enter your message"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900 placeholder-gray-500"
          ></textarea>
          <div class="absolute bottom-2 right-2 text-sm text-gray-500">
            {{ message.length }}/500
          </div>
        </div>
      </div>

      <!-- Schedule Options -->
      <div class="space-y-4">
        <label class="block text-sm font-medium text-gray-900">Schedule</label>
        <div class="grid grid-cols-1 md:grid-cols-1 gap-4">
          <button
            @click="scheduleType = 'now'"
            class="p-4 rounded-lg border-2 transition-all duration-200 flex items-center"
            :class="[
              scheduleType === 'now'
                ? 'border-maroon-600 bg-maroon-50'
                : 'border-gray-200 hover:border-gray-300',
            ]"
          >
            <span
              class="p-2 rounded-lg mr-3"
              :class="scheduleType === 'now' ? 'bg-maroon-100' : 'bg-gray-100'"
            >
              <span
                class="material-icons"
                :class="scheduleType === 'now' ? 'text-maroon-600' : 'text-gray-500'"
                >send</span
              >
            </span>
            <div class="text-left">
              <div class="font-medium text-gray-900">Send Now</div>
              <div class="text-sm text-gray-600">Notify recipients immediately</div>
            </div>
          </button>

          <!-- <button
            @click="scheduleType = 'schedule'"
            class="p-4 rounded-lg border-2 transition-all duration-200 flex items-center"
            :class="[
              scheduleType === 'schedule'
                ? 'border-maroon-600 bg-maroon-50'
                : 'border-gray-200 hover:border-gray-300',
            ]"
          >
            <span
              class="p-2 rounded-lg mr-3"
              :class="scheduleType === 'schedule' ? 'bg-maroon-100' : 'bg-gray-100'"
            >
              <span
                class="material-icons"
                :class="scheduleType === 'schedule' ? 'text-maroon-600' : 'text-gray-500'"
                >schedule</span
              >
            </span>
            <div class="text-left">
              <div class="font-medium text-gray-900">Schedule</div>
              <div class="text-sm text-gray-600">Send at a specific date & time</div>
            </div>
          </button> -->
        </div>

        <!-- Schedule DateTime -->
        <div v-if="scheduleType === 'schedule'" class="space-y-2">
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="material-icons text-gray-400">event</span>
            </span>
            <input
              type="datetime-local"
              v-model="scheduledDateTime"
              :min="minScheduleDateTime"
              class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 text-gray-900"
            />
          </div>
        </div>
      </div>

      <!-- Preview -->
      <div v-if="isFormValid" class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div class="text-sm font-medium text-gray-900 mb-2">Preview</div>
        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <span
              class="px-2 py-1 rounded-full text-xs font-medium"
              :class="getPriorityClass(priority)"
            >
              {{ getPriorityLabel(priority) }}
            </span>
            <span class="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              {{ getCategoryLabel(category) }}
            </span>
          </div>
          <div class="font-medium text-gray-900">{{ title || 'Notification Title' }}</div>
          <div class="text-gray-600 text-sm">
            {{ message || 'Notification message will appear here' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="p-6 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
      <button
        @click="resetForm"
        class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
      >
        <span class="material-icons text-sm mr-1">refresh</span>
        Reset
      </button>

      <div class="flex items-center space-x-3">
        <span v-if="!isFormValid" class="text-sm text-gray-500">
          Please fill in all required fields
        </span>
        <button
          @click="sendNotification"
          class="px-6 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!isFormValid"
        >
          <span class="material-icons text-sm mr-1">
            {{ scheduleType === 'schedule' ? 'schedule_send' : 'send' }}
          </span>
          {{ scheduleType === 'schedule' ? 'Schedule' : 'Send' }} Notification
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationForm',
  props: {
    isAdmin: {
      type: Boolean,
      default: false,
    },
    courses: {
      type: Array,
      default: () => [],
    },
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
      scheduledDateTime: null,
      priorityLevels: [
        {
          value: 'low',
          label: 'Low',
          icon: 'arrow_downward',
          color: 'green',
          activeClasses: 'bg-green-50',
        },
        {
          value: 'medium',
          label: 'Medium',
          icon: 'remove',
          color: 'blue',
          activeClasses: 'bg-blue-50',
        },
        {
          value: 'high',
          label: 'High',
          icon: 'arrow_upward',
          color: 'orange',
          activeClasses: 'bg-orange-50',
        },
        {
          value: 'urgent',
          label: 'Urgent',
          icon: 'warning',
          color: 'red',
          activeClasses: 'bg-red-50',
        },
      ],
    }
  },
  computed: {
    showSystemOption() {
      return this.isAdmin
    },
    isFormValid() {
      const baseValidation =
        this.title.trim() && this.message.trim() && this.priority && this.category

      if (this.notificationType === 'course') {
        return baseValidation && this.selectedCourse
      }

      if (this.scheduleType === 'schedule') {
        return baseValidation && this.scheduledDateTime
      }

      return baseValidation
    },
    minScheduleDateTime() {
      const now = new Date()
      now.setMinutes(now.getMinutes() + 5) // Minimum 5 minutes from now
      return now.toISOString().slice(0, 16)
    },
    availableCategories() {
      const baseCategories = [
        { value: 'announcement', label: 'Announcement' },
        { value: 'assignment', label: 'Assignment' },
        // { value: 'reminder', label: 'Reminder' },
        { value: 'grade', label: 'Grade' },
      ]

      if (this.notificationType === 'system') {
        return [
          ...baseCategories,
          { value: 'maintenance', label: 'System Maintenance' },
          { value: 'technical', label: 'Technical Issue' },
        ]
      }

      return baseCategories
    },
  },
  watch: {
    isAdmin: {
      immediate: true,
      handler(newValue) {
        if (!newValue && this.notificationType === 'system') {
          this.notificationType = 'course'
        }
      },
    },
  },
  methods: {
    async sendNotification() {
      try {
        if (!this.isAdmin && this.notificationType === 'system') {
          this.$toast.error('You do not have permission to send system-wide notifications')
          return
        }

        const notification = {
          type: this.notificationType,
          courseId: this.selectedCourse,
          priority: this.priority,
          category: this.category,
          title: this.title,
          message: this.message,
          // scheduleType: this.scheduleType,
          // scheduledDateTime: this.scheduledDateTime,
        }

        await this.$emit('send-notification', notification)
        // this.$toast.success(
        //   `Notification ${this.scheduleType === 'schedule' ? 'scheduled' : 'sent'} successfully`,
        // )
        this.resetForm()
      } catch (error) {
        // this.$toast.error('Failed to send notification')
        console.log(error)
      }
    },
    resetForm() {
      this.notificationType = 'course'
      this.selectedCourse = ''
      this.priority = 'medium'
      this.category = 'announcement'
      this.title = ''
      this.message = ''
      // this.scheduleType = 'now'
      // this.scheduledDateTime = null
    },
    getPriorityClass(priority) {
      const classes = {
        low: 'bg-green-100 text-green-800',
        medium: 'bg-blue-100 text-blue-800',
        high: 'bg-orange-100 text-orange-800',
        urgent: 'bg-red-100 text-red-800',
      }
      return classes[priority] || classes.medium
    },
    getPriorityLabel(priority) {
      return this.priorityLevels.find((level) => level.value === priority)?.label || 'Medium'
    },
    getCategoryLabel(category) {
      return this.availableCategories.find((cat) => cat.value === category)?.label || 'Announcement'
    },
  },
}
</script>

<style scoped>
.material-icons {
  font-size: inherit;
  line-height: inherit;
  vertical-align: middle;
}

/* Custom styles for datetime-local input */
input[type='datetime-local']::-webkit-calendar-picker-indicator {
  background: transparent;
  bottom: 0;
  color: transparent;
  cursor: pointer;
  height: auto;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  width: auto;
}
</style>
