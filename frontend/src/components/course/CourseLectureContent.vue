<template>
  <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
    <div class="xl:col-span-2 space-y-8">
      <!-- Lecture Info -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <div class="flex items-start justify-between">
          <div class="space-y-3">
            <h2 class="text-2xl font-bold text-gray-900">{{ lecture.title }}</h2>
            <p class="text-gray-600 leading-relaxed">{{ lecture.description }}</p>
          </div>
          <div class="relative w-20 h-20">
            <svg class="progress-ring" width="80" height="80">
              <circle class="text-gray-200" stroke-width="6" fill="transparent" r="37" cx="40" cy="40"/>
              <circle class="text-primary-500" stroke-width="6" :stroke-dasharray="`${lecture.progress * 2.34}, 234`" 
                      fill="transparent" r="37" cx="40" cy="40" style="filter: drop-shadow(0 0 8px rgba(2, 132, 199, 0.2))"/>
            </svg>
            <button @click="$emit('mark-complete')" 
                    class="absolute inset-0 flex items-center justify-center w-full h-full
                           transition-transform duration-300 hover:scale-105">
              <i class="fas text-2xl" 
                 :class="lecture.completed ? 'fa-check-circle text-green-500' : 'fa-circle-play text-primary-500'"></i>
            </button>
          </div>
        </div>
        
        <div class="mt-6 flex flex-wrap gap-3">
          <button class="px-5 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 
                    transition-all duration-300 flex items-center space-x-2 shadow-md hover:shadow-lg">
            <i class="fas fa-download"></i>
            <span>Resources</span>
          </button>
        </div>
      </div>

      <!-- Key Concepts -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-5">Key Concepts</h3>
        <ul class="space-y-4">
          <li v-for="(objective, index) in lecture.objectives" :key="index"
              class="flex items-start space-x-3 p-3 bg-gray-50/50 rounded-lg hover:bg-gray-50 transition-colors">
            <i class="fas fa-check-circle text-green-500 mt-1"></i>
            <span class="text-gray-700 leading-relaxed">{{ objective }}</span>
          </li>
        </ul>
      </div>

      <!-- Discussion -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-5">Community Dialogue</h3>
        <div class="space-y-5">
          <textarea
            placeholder="Engage with peers..."
            class="w-full p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 
                   focus:border-transparent transition-all duration-300 resize-none"
            rows="3"
          ></textarea>
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2 text-gray-500">
              <button class="p-2 hover:bg-gray-100 rounded-lg">
                <i class="fas fa-paperclip"></i>
              </button>
              <button class="p-2 hover:bg-gray-100 rounded-lg">
                <i class="fas fa-at"></i>
              </button>
            </div>
            <button class="px-6 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 
                      transition-all duration-300 flex items-center space-x-2 shadow-md">
              <i class="fas fa-paper-plane"></i>
              <span>Post</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Sidebar Content -->
    <div class="space-y-8">
      <!-- Resources -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-5">Learning Toolkit</h3>
        <ul class="space-y-3">
          <li v-for="(material, index) in lecture.materials" :key="index"
              class="flex items-center justify-between p-3 bg-gray-50/50 rounded-lg hover:bg-gray-50 
                    transition-colors cursor-pointer group">
            <div class="flex items-center space-x-3">
              <i class="fas text-lg transform transition-all"
                 :class="[getFileIcon(material.type), 'group-hover:scale-110']"></i>
              <span class="text-sm font-medium text-gray-700">{{ material.title }}</span>
            </div>
            <button class="p-2 hover:bg-gray-200 rounded-lg transition-colors">
              <i class="fas fa-download text-gray-600"></i>
            </button>
          </li>
        </ul>
      </div>

      <!-- Challenges -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-5">Skill Challenges</h3>
        <ul class="space-y-4">
          <li v-for="(question, index) in lecture.questions" :key="index"
              class="p-3 bg-gray-50/50 rounded-lg hover:bg-gray-50 transition-colors">
            <div class="flex items-start space-x-3">
              <span class="flex-shrink-0 w-7 h-7 bg-primary-100 text-primary-600 rounded-lg flex items-center 
                       justify-center text-sm font-bold">
                {{ index + 1 }}
              </span>
              <p class="text-gray-700 leading-relaxed">{{ question }}</p>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseLectureContent',
  props: {
    lecture: {
      type: Object,
      required: true
    },
    getFileIcon: {
      type: Function,
      required: true
    }
  },
  emits: ['mark-complete']
}
</script> 