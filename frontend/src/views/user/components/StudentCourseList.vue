<!-- src/views/user/components/StudentCourseList.vue -->
<template>
  <div class="student-course-list space-y-4">
    <div v-for="course in courses" 
         :key="course.id" 
         class="course-item bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
    >
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3">
            <h3 class="text-lg font-semibold text-gray-800">{{ course.title }}</h3>
            <span 
              class="text-sm px-2 py-1 rounded-full"
              :class="{
                'bg-green-100 text-green-800': course.progress === 100,
                'bg-blue-100 text-blue-800': course.progress > 0 && course.progress < 100,
                'bg-gray-100 text-gray-800': course.progress === 0
              }"
            >
              {{ course.progress === 100 ? 'Completed' : course.progress > 0 ? 'In Progress' : 'Not Started' }}
            </span>
          </div>
          
          <p class="text-gray-600 text-sm mt-2">{{ course.description }}</p>
          
          <div class="flex items-center space-x-6 mt-4">
            <div class="flex items-center space-x-2">
              <img 
                :src="course.instructor.avatar" 
                :alt="course.instructor.name"
                class="w-8 h-8 rounded-full object-cover"
              >
              <span class="text-sm text-gray-600">{{ course.instructor.name }}</span>
            </div>
            
            <span class="text-sm text-gray-500">
              <i class="fas fa-clock mr-1"></i>
              {{ course.duration }}
            </span>
            
            <div class="flex items-center space-x-1">
              <i class="fas fa-star text-yellow-400"></i>
              <span class="text-sm text-gray-600">{{ course.rating || 0 }}</span>
            </div>
          </div>
          
          <!-- Progress bar -->
          <div class="mt-4">
            <div class="flex items-center justify-between text-sm mb-1">
              <span class="text-gray-600">Progress</span>
              <span class="font-medium">{{ course.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-maroon-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${course.progress}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="flex flex-col items-end space-y-2">
          <button 
            class="text-maroon-600 hover:text-maroon-700"
            @click="$emit('toggle-bookmark', course)"
          >
            <i class="fas" :class="course.isBookmarked ? 'fa-bookmark' : 'fa-bookmark-o'"></i>
          </button>
          
          <button 
            class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
            @click="$emit('continue-course', course)"
          >
            {{ course.progress > 0 ? 'Continue' : 'Start' }}
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="!courses.length" class="text-center py-8 bg-white rounded-xl shadow-sm border border-gray-100">
      <p class="text-gray-500">No courses enrolled yet</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentCourseList',
  props: {
    courses: {
      type: Array,
      required: true
    }
  },
  emits: ['toggle-bookmark', 'continue-course']
};
</script>

<style scoped>
.course-item:hover {
  border-color: #9f1239;
}
</style> 