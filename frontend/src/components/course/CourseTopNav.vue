<template>
  <div class="bg-white border-b border-gray-200/80 px-4 sm:px-6 py-4 shadow-sm backdrop-blur-sm">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-3 sm:space-y-0">
      <div class="flex items-center space-x-3">
        <button @click="$router.go(-1)" class="p-2 hover:bg-gray-100/80 rounded-lg transition-all duration-300
                 text-gray-600 hover:text-primary-600 active:scale-95">
          <i class="fas fa-arrow-left text-lg"></i>
        </button>
        <div class="space-y-0.5">
          <h1 class="text-2xl font-bold text-gray-900 tracking-tight">{{ course.title }}</h1>
          <div class="flex items-center space-x-2">
            <i class="fas fa-chalkboard-teacher text-gray-400 text-sm"></i>
            <p class="text-sm text-gray-600 font-medium">{{ course.instructor?.name }}</p>
          </div>
        </div>
      </div>
      
      <div class="flex items-center space-x-4 sm:space-x-5">
        <div class="flex items-center space-x-3 bg-gray-50 px-4 py-2 rounded-xl">
          <div class="relative w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-500"
                 :style="{ width: `${course.progress || 0}%` }"></div>
          </div>
          <span class="text-sm font-semibold text-primary-600">{{ course.progress || 0 }}%</span>
        </div>
        <div class="flex items-center space-x-2">
          <button @click="$emit('toggle-bookmark')" 
                  class="p-2.5 hover:bg-gray-100/80 rounded-xl transition-all duration-300
                         text-gray-600 hover:text-primary-600 active:scale-95"
                  :class="{'text-primary-600': isBookmarked}">
            <i class="fas fa-bookmark text-lg"></i>
          </button>
          <button @click="$emit('toggle-notes')" 
                  class="p-2.5 hover:bg-gray-100/80 rounded-xl transition-all duration-300
                         text-gray-600 hover:text-primary-600 active:scale-95">
            <i class="fas fa-sticky-note text-lg"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseTopNav',
  props: {
    course: {
      type: Object,
      required: true
    },
    isBookmarked: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-bookmark', 'toggle-notes']
}
</script> 