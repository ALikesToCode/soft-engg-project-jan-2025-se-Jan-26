<template>
  <div class="sticky top-0 z-10 bg-white border-b border-slate-200 shadow-sm">
    <div class="px-6 py-4">
      <div class="flex items-center justify-between">
        <!-- Left Section -->
        <div class="flex items-center space-x-4">
          <button @click="$emit('back-to-courses')" 
                  class="p-2 rounded-lg hover:bg-maroon-50 text-slate-600 hover:text-maroon-600 transition-colors">
            <span class="material-symbols-outlined">arrow_back</span>
          </button>
          <div class="flex flex-col">
            <h1 class="text-xl font-bold text-slate-900">{{ course.title }}</h1>
            <div class="flex items-center space-x-2 mt-1">
              <span class="material-symbols-outlined text-maroon-400">person</span>
              <div class="flex items-center space-x-2">
                <span class="text-sm font-medium text-slate-700">{{ course.instructor?.name }}</span>
                <span class="text-xs text-slate-500">{{ course.instructor?.title }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Section -->
        <div class="flex items-center space-x-6">
          <!-- Progress Section -->
          <div class="flex items-center space-x-3">
            <div class="w-32 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-maroon-500 to-maroon-600 rounded-full transition-all duration-500"
                   :style="{ width: `${progress}%` }"></div>
            </div>
            <span class="text-sm font-medium text-slate-700">{{ progress }}%</span>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center space-x-2">
            <button @click="$emit('toggle-bookmark')"
                    class="p-2 rounded-lg hover:bg-maroon-50 transition-colors"
                    :class="isBookmarked ? 'text-yellow-500' : 'text-slate-400 hover:text-maroon-600'">
              <span class="material-symbols-outlined" :class="{ 'filled': isBookmarked }">bookmark</span>
            </button>
            <button @click="$emit('toggle-notes')"
                    class="p-2 rounded-lg hover:bg-maroon-50 text-slate-400 hover:text-maroon-600 transition-colors">
              <span class="material-symbols-outlined">edit_note</span>
            </button>
          </div>
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
    },
    progress: {
      type: Number,
      default: 0
    }
  },
  emits: ['back-to-courses', 'toggle-bookmark', 'toggle-notes']
}
</script>

<style scoped>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}

.material-symbols-outlined.filled {
  font-variation-settings:
    'FILL' 1,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
}
</style> 