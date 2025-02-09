<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 overflow-hidden">
      <div class="h-full flex">
        <!-- Main Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Header -->
          <div class="max-w-5xl mx-auto mb-8">
            <div class="flex items-center justify-between">
              <div>
                <h1 class="text-3xl font-bold text-gray-900">{{ roadmap.title }}</h1>
                <p class="text-gray-600 mt-1">{{ roadmap.description }}</p>
              </div>
              <div class="flex items-center space-x-4">
                <div class="text-right">
                  <div class="text-sm text-gray-600">Overall Progress</div>
                  <div class="text-2xl font-bold text-gray-900">
                    {{ Math.round((roadmap.completedSteps / roadmap.totalSteps) * 100) }}%
                  </div>
                </div>
                <div class="h-16 w-16 rounded-full bg-maroon-100 flex items-center justify-center">
                  <span class="material-icons text-maroon-600 text-2xl">timeline</span>
                </div>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-4">
              <div class="flex items-center justify-between text-sm mb-2">
                <span class="font-medium text-gray-900">Learning Progress</span>
                <span class="text-gray-600">{{ roadmap.completedSteps }} of {{ roadmap.totalSteps }} Steps Completed</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-2.5">
                <div 
                  class="bg-maroon-600 h-2.5 rounded-full transition-all duration-500"
                  :style="{ width: `${(roadmap.completedSteps / roadmap.totalSteps) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Roadmap Timeline -->
          <div class="max-w-5xl mx-auto">
            <div class="space-y-8">
              <div 
                v-for="(milestone, index) in roadmap.milestones" 
                :key="milestone.id"
                class="relative"
              >
                <!-- Timeline Line -->
                <div 
                  v-if="index < roadmap.milestones.length - 1"
                  class="absolute left-8 top-14 bottom-0 w-0.5 bg-gray-200"
                ></div>

                <!-- Milestone Card -->
                <div 
                  class="bg-white rounded-xl shadow-sm border border-gray-100 relative"
                  :class="{ 'opacity-60': milestone.locked }"
                >
                  <!-- Milestone Header -->
                  <div class="p-6 flex items-start space-x-4">
                    <div 
                      class="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0"
                      :class="getMilestoneStatusClasses(milestone.status).bgClass"
                    >
                      <span 
                        class="material-icons text-2xl"
                        :class="getMilestoneStatusClasses(milestone.status).textClass"
                      >
                        {{ getMilestoneStatusIcon(milestone.status) }}
                      </span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between">
                        <div>
                          <h3 class="text-xl font-semibold text-gray-900">{{ milestone.title }}</h3>
                          <p class="text-gray-600 mt-1">{{ milestone.description }}</p>
                        </div>
                        <div class="text-right">
                          <span 
                            class="px-3 py-1 rounded-full text-sm font-medium"
                            :class="getMilestoneStatusClasses(milestone.status).badgeClass"
                          >
                            {{ milestone.status }}
                          </span>
                          <div class="text-sm text-gray-500 mt-1">
                            {{ milestone.estimatedTime }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Learning Materials -->
                  <div v-if="milestone.materials && milestone.materials.length > 0" class="px-6 pb-6">
                    <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div
                        v-for="material in milestone.materials"
                        :key="material.id"
                        class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
                      >
                        <div class="flex items-start space-x-3">
                          <div 
                            class="p-2 rounded-lg"
                            :class="getMaterialTypeClasses(material.type).bgClass"
                          >
                            <span 
                              class="material-icons"
                              :class="getMaterialTypeClasses(material.type).textClass"
                            >
                              {{ getMaterialTypeIcon(material.type) }}
                            </span>
                          </div>
                          <div class="flex-1 min-w-0">
                            <h4 class="font-medium text-gray-900">{{ material.title }}</h4>
                            <p class="text-sm text-gray-600 mt-1">{{ material.description }}</p>
                            <div class="flex items-center space-x-4 mt-2">
                              <button 
                                @click="startLearning(material)"
                                class="text-sm text-maroon-600 hover:text-maroon-700 font-medium inline-flex items-center"
                                :disabled="milestone.locked"
                              >
                                Start Learning
                                <span class="material-icons text-sm ml-1">arrow_forward</span>
                              </button>
                              <span class="text-sm text-gray-500">{{ material.duration }}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Panel -->
        <div 
          class="w-96 border-l border-gray-200 bg-white flex flex-col"
          :class="{ 'hidden': !showChat }"
        >
          <div class="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Learning Assistant</h2>
            <button 
              @click="showChat = false"
              class="p-1 hover:bg-gray-100 rounded-full transition-colors"
            >
              <span class="material-icons text-gray-500">close</span>
            </button>
          </div>
          <ChatBotBox class="flex-1" :context="currentLearningContext" />
        </div>

        <!-- Toggle Chat Button -->
        <button
          v-if="!showChat"
          @click="showChat = true"
          class="fixed bottom-6 right-6 bg-maroon-600 text-white rounded-full p-4 shadow-lg hover:bg-maroon-700 transition-all z-10"
        >
          <span class="material-icons">chat</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import SideNavBar from '@/layouts/SideNavBar.vue'
import ChatBotBox from '@/components/ChatBotBox.vue'
import { useChatStore } from '@/stores/useChatStore'

export default {
  name: 'RoadmapView',
  components: {
    SideNavBar,
    ChatBotBox
  },
  setup() {
    const chatStore = useChatStore()
    return {
      chatStore
    }
  },
  data() {
    return {
      showChat: false,
      currentLearningContext: null,
      roadmap: {
        id: 1,
        title: 'Full Stack Development Path',
        description: 'Master full stack development with this comprehensive learning path',
        completedSteps: 5,
        totalSteps: 12,
        milestones: [
          {
            id: 1,
            title: 'Frontend Fundamentals',
            description: 'Learn the basics of HTML, CSS, and JavaScript',
            status: 'completed',
            estimatedTime: '4 weeks',
            locked: false,
            materials: [
              {
                id: 1,
                type: 'video',
                title: 'HTML & CSS Basics',
                description: 'Introduction to web development fundamentals',
                duration: '2 hours',
                url: '/course/web-dev/html-css'
              },
              {
                id: 2,
                type: 'exercise',
                title: 'JavaScript Exercises',
                description: 'Practice JavaScript fundamentals with hands-on exercises',
                duration: '3 hours',
                url: '/course/web-dev/js-exercises'
              }
            ]
          },
          {
            id: 2,
            title: 'Vue.js Framework',
            description: 'Master modern frontend development with Vue.js',
            status: 'in_progress',
            estimatedTime: '6 weeks',
            locked: false,
            materials: [
              {
                id: 3,
                type: 'course',
                title: 'Vue.js Fundamentals',
                description: 'Learn Vue.js core concepts and best practices',
                duration: '8 hours',
                url: '/course/vue/fundamentals'
              },
              {
                id: 4,
                type: 'project',
                title: 'Build a Vue.js App',
                description: 'Create a real-world application using Vue.js',
                duration: '10 hours',
                url: '/course/vue/project'
              }
            ]
          },
          {
            id: 3,
            title: 'Backend Development',
            description: 'Learn server-side programming and databases',
            status: 'locked',
            estimatedTime: '8 weeks',
            locked: true,
            materials: [
              {
                id: 5,
                type: 'course',
                title: 'Node.js Basics',
                description: 'Introduction to server-side JavaScript',
                duration: '6 hours',
                url: '/course/backend/nodejs'
              },
              {
                id: 6,
                type: 'tutorial',
                title: 'Database Design',
                description: 'Learn SQL and database fundamentals',
                duration: '4 hours',
                url: '/course/backend/database'
              }
            ]
          }
        ]
      }
    }
  },
  methods: {
    getMilestoneStatusClasses(status) {
      const classes = {
        completed: {
          bgClass: 'bg-green-100',
          textClass: 'text-green-600',
          badgeClass: 'bg-green-100 text-green-800'
        },
        in_progress: {
          bgClass: 'bg-blue-100',
          textClass: 'text-blue-600',
          badgeClass: 'bg-blue-100 text-blue-800'
        },
        locked: {
          bgClass: 'bg-gray-100',
          textClass: 'text-gray-600',
          badgeClass: 'bg-gray-100 text-gray-800'
        }
      }
      return classes[status] || classes.locked
    },
    getMilestoneStatusIcon(status) {
      const icons = {
        completed: 'check_circle',
        in_progress: 'trending_up',
        locked: 'lock'
      }
      return icons[status] || 'help'
    },
    getMaterialTypeClasses(type) {
      const classes = {
        video: {
          bgClass: 'bg-purple-100',
          textClass: 'text-purple-600'
        },
        exercise: {
          bgClass: 'bg-orange-100',
          textClass: 'text-orange-600'
        },
        course: {
          bgClass: 'bg-blue-100',
          textClass: 'text-blue-600'
        },
        project: {
          bgClass: 'bg-green-100',
          textClass: 'text-green-600'
        },
        tutorial: {
          bgClass: 'bg-yellow-100',
          textClass: 'text-yellow-600'
        }
      }
      return classes[type] || classes.course
    },
    getMaterialTypeIcon(type) {
      const icons = {
        video: 'play_circle',
        exercise: 'assignment',
        course: 'school',
        project: 'engineering',
        tutorial: 'menu_book'
      }
      return icons[type] || 'article'
    },
    startLearning(material) {
      this.chatStore.setContext({
        type: material.type,
        title: material.title,
        description: material.description,
        url: material.url
      })
      this.$router.push(material.url)
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style> 