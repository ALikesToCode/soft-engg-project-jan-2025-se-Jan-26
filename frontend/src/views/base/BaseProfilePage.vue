<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Profile Header -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div class="flex items-start space-x-6">
          <!-- Profile Picture Section -->
          <div class="relative">
            <img 
              :src="userInfo.profilePictureUrl" 
              :alt="userInfo.name"
              class="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
            />
            <button
              v-if="isEditable"
              @click="handleProfilePictureUpdate"
              class="absolute bottom-0 right-0 p-2 rounded-full bg-maroon-600 hover:bg-maroon-700 text-white shadow-lg transition-colors focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2"
              aria-label="Update profile picture"
            >
              <span class="material-icons text-sm">photo_camera</span>
            </button>
            <input
              ref="profilePictureInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="onProfilePictureSelected"
            />
          </div>

          <!-- User Info -->
          <div class="flex-1">
            <div class="flex items-center justify-between">
              <div>
                <h1 class="text-2xl font-bold text-gray-900">{{ userInfo.name }}</h1>
                <p class="text-gray-600">{{ userInfo.email }}</p>
                <p v-if="userInfo.department" class="text-gray-600">{{ userInfo.department }}</p>
              </div>
              <button
                v-if="isEditable"
                @click="$emit('edit-profile')"
                class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors flex items-center space-x-2"
              >
                <span class="material-icons text-sm">edit</span>
                <span>Edit Profile</span>
              </button>
            </div>

            <!-- Role-specific Stats -->
            <div v-if="showStats" class="mt-4 flex items-center space-x-6">
              <div v-if="userType !== 'student'" class="flex items-center space-x-2">
                <span class="material-icons text-maroon-600">school</span>
                <div>
                  <div class="text-sm font-medium text-gray-600">Courses</div>
                  <div class="text-lg font-semibold text-gray-900">{{ userInfo.coursesCount }}</div>
                </div>
              </div>
              
              <div v-if="userType === 'faculty'" class="flex items-center space-x-2">
                <span class="material-icons text-maroon-600">groups</span>
                <div>
                  <div class="text-sm font-medium text-gray-600">Students</div>
                  <div class="text-lg font-semibold text-gray-900">{{ userInfo.studentsCount }}</div>
                </div>
              </div>

              <div v-if="userType === 'faculty'" class="flex items-center space-x-2">
                <span class="material-icons text-maroon-600">star</span>
                <div>
                  <div class="text-sm font-medium text-gray-600">Rating</div>
                  <div class="text-lg font-semibold text-gray-900">{{ userInfo.rating }}/5.0</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Role-specific content -->
      <div class="mt-6">
        <slot name="role-content">
          <!-- Default content if no role-specific content is provided -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <p class="text-gray-600">No specific content available for this role.</p>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseProfilePage',
  props: {
    userType: {
      type: String,
      required: true,
      validator: (value) => ['faculty', 'student', 'support'].includes(value)
    },
    userInfo: {
      type: Object,
      required: true
    },
    isEditable: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    showStats() {
      return this.userType === 'faculty' || (this.userType === 'support' && this.userInfo.coursesCount)
    }
  },
  methods: {
    handleProfilePictureUpdate() {
      this.$refs.profilePictureInput.click()
    },
    async onProfilePictureSelected(event) {
      const file = event.target.files[0]
      if (!file) return

      // Validate file type and size
      if (!file.type.startsWith('image/')) {
        this.$toast.error('Please select an image file')
        return
      }

      const maxSize = 5 * 1024 * 1024 // 5MB
      if (file.size > maxSize) {
        this.$toast.error('Image size should be less than 5MB')
        return
      }

      try {
        // Here you would typically upload the file to your server
        // For now, we'll just emit an event that parent components can handle
        this.$emit('update-profile-picture', file)
        this.$toast.success('Profile picture updated successfully')
      } catch (error) {
        this.$toast.error('Failed to update profile picture')
      }

      // Clear the input
      event.target.value = ''
    }
  }
}
</script> 