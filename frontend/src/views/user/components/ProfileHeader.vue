<!-- src/views/user/components/ProfileHeader.vue -->
<template>
  <div class="profile-header bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center space-x-6">
      <div class="relative">
        <img 
          :src="user.profilePictureUrl || '/images/default-avatar.png'" 
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
        
        <div class="mt-4 flex space-x-6">
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
            <p class="text-sm text-gray-600">Rating</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileHeader',
  props: {
    user: {
      type: Object,
      required: true
    },
    isEditable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update-photo', 'edit-profile']
};
</script>

<style scoped>
.profile-header {
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(10px);
}
</style> 