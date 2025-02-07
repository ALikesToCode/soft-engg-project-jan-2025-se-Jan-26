<!-- src/views/user/components/ContentOrderingPreview.vue -->
<template>
  <div class="content-ordering-preview bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-gray-800">Course Order Preview</h2>
      <div class="text-sm text-gray-500">
        {{ courses.length }} {{ courses.length === 1 ? 'Course' : 'Courses' }}
      </div>
    </div>
    
    <div class="space-y-3">
      <div v-for="(course, index) in courses" 
           :key="course.id"
           class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg"
      >
        <div class="flex-shrink-0 w-8 h-8 bg-maroon-600 text-white rounded-full flex items-center justify-center font-semibold">
          {{ index + 1 }}
        </div>
        
        <div class="flex-1 min-w-0">
          <h3 class="text-gray-800 font-medium truncate">{{ course.title }}</h3>
          <p class="text-gray-500 text-sm truncate">{{ course.description }}</p>
        </div>
        
        <div class="flex-shrink-0">
          <span 
            class="text-sm px-2 py-1 rounded-full"
            :class="{
              'bg-green-100 text-green-800': course.status === 'active',
              'bg-yellow-100 text-yellow-800': course.status === 'draft',
              'bg-gray-100 text-gray-800': course.status === 'archived'
            }"
          >
            {{ course.status }}
          </span>
        </div>
      </div>
    </div>
    
    <div v-if="!courses.length" class="text-center py-8">
      <p class="text-gray-500">No courses to preview</p>
    </div>
    
    <div v-if="courses.length > 0" class="mt-6 pt-4 border-t border-gray-100">
      <p class="text-sm text-gray-500">
        <i class="fas fa-info-circle mr-2"></i>
        This preview shows how your courses will appear to students
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContentOrderingPreview',
  props: {
    courses: {
      type: Array,
      required: true
    }
  }
};
</script>

<style scoped>
.content-ordering-preview {
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(10px);
}
</style> 