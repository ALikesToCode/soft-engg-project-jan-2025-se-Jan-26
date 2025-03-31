<!-- src/views/user/components/ProfileHeader.vue -->
<template>
  <div class="profile-header bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center space-x-6">
      <div class="relative">
        <img
          :src="profileImageSrc"
          :alt="`${user.name}'s Profile Picture`"
          class="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
        />
        <button
          v-if="isEditable"
          class="absolute bottom-0 right-0 bg-maroon-600 text-white p-2 rounded-full shadow-lg hover:bg-maroon-700 transition-colors"
          @click="$emit('update-photo')"
        >
          <i class="fas fa-camera text-sm"></i>
        </button>
      </div>

      <div class="flex-1">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-800">{{ user.name }}</h1>
            <p class="text-gray-600">{{ user.email }}</p>
            <p v-if="user.department" class="text-gray-600 text-sm mt-1">
              {{ user.department }}
            </p>
          </div>
          <button
            v-if="isEditable"
            class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
            @click="$emit('edit-profile')"
          >
            Edit Profile
          </button>
        </div>

        <div v-if="userType !== 'support'" class="mt-4 flex space-x-6">
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-800">{{ user.coursesCount || 0 }}</p>
            <p class="text-sm text-gray-600">Courses</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-800">{{ user.studentsCount || 0 }}</p>
            <p class="text-sm text-gray-600">Students</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-800">{{ user.rating || 0 }}</p>
            <p v-if="userType === 'student'" class="text-sm text-gray-600">CGPA</p>
            <p v-else class="text-sm text-gray-600">Rating</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Base64 dummy image as a reliable fallback
const dummyAvatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=="

export default {
  name: 'ProfileHeader',
  props: {
    user: {
      type: Object,
      required: true,
    },
    userType: {
      type: String,
      required: true,
    },
    isEditable: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    profileImageSrc() {
      // Use profile picture URL if available
      if (this.user.profilePictureUrl) {
        return this.user.profilePictureUrl
      }
      
      // Use base64 encoded SVG as a guaranteed fallback
      return dummyAvatar
    }
  },
  emits: ['update-photo', 'edit-profile'],
}
</script>

<style scoped>
.profile-header {
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(10px);
}
</style>
