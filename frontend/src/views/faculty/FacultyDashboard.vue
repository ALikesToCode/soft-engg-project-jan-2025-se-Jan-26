<script>
import ChatBotWrapper from '@/components/ChatBotWrapper.vue'
import SideNavBar from '@/layouts/SideNavBar.vue'
export default {
  name: 'FacultyDashboard',
  data() {
    return {
      queryEmpty: true,
      showSplitScreen: false,
      courses: ['Math', 'CT', 'SE', 'ST'],
      months: ['January 2025', 'February 2025', 'March 2025'],
      selectedCourse: '',
      selectedMonth: '',
      topics: [
        { id: 1, name: 'Machine Learning Basics', accessCount: 120, trend: 'up' },
        { id: 2, name: 'Data Structures', accessCount: 95, trend: 'down' },
        { id: 3, name: 'Deep Learning Fundamentals', accessCount: 78, trend: 'up' },
        { id: 4, name: 'Cloud Computing', accessCount: 60, trend: 'down' },
        { id: 5, name: 'Cybersecurity Essentials', accessCount: 130, trend: 'up' },
        { id: 6, name: 'Operating Systems', accessCount: 88, trend: 'down' },
      ],
    }
  },
  components: {
    ChatBotWrapper,
    SideNavBar,
  },
  computed: {
    mainContentClass() {
      return {
        // 'md:grid-cols-1': !this.showSplitScreen,
        'md:grid-cols-3': this.showSplitScreen,
      }
    },
  },
  methods: {
    toggleSplitScreen() {
      this.showSplitScreen = !this.showSplitScreen
    },
  },
}
</script>

<template>
  <div class="flex h-screen">
    <div>
      <SideNavBar />
    </div>
    <div class="flex-1 p-6 overflow-y-auto bg-gray-50">
      <!-- Main Section -->
      <div class="grid" :class="mainContentClass" gap-6>
        <div class="flex gap-4 mb-4 mx-auto">
          <select v-model="selectedCourse" class="flex-1 px-4 py-2 bg-red-700 text-white rounded">
            <option disabled value="">Course</option>
            <option v-for="course in courses" :key="course">{{ course }}</option>
          </select>

          <select v-model="selectedMonth" class="flex-1 px-4 py-2 bg-red-700 text-white rounded">
            <option disabled value="">Month/Year</option>
            <option v-for="month in months" :key="month">{{ month }}</option>
          </select>
        </div>
        <div class="space-y-4 mx-auto">
          <div class="p-4 border rounded-lg bg-white">
            Aggregated Insights (Common Student Engagement and Challenges)
          </div>

          <!-- Frequently Accessed Topics insights -->
          <div class="px-2 sm:px-4 py-2 border rounded-lg bg-white">
            <div class="px-2 sm:px-4 py-2">
              <h1 class="text-2xl font-semibold text-gray-700 mb-4 text-center">
                Frequently Accessed Topics
              </h1>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                <div
                  v-for="topic in topics"
                  :key="topic.id"
                  class="p-4 bg-white rounded-lg shadow-md border border-gray-200 transition-transform transform hover:scale-105"
                >
                  <h3 class="text-lg font-semibold text-gray-600">{{ topic.name }}</h3>
                  <p class="text-sm text-gray-600">Accessed {{ topic.accessCount }} times</p>

                  <div class="mt-2 flex items-center space-x-2">
                    <span
                      class="px-2 py-1 text-xs font-semibold rounded-full"
                      :class="{
                        'bg-green-100 text-green-800': topic.trend === 'up',
                        'bg-red-100 text-red-800': topic.trend === 'down',
                      }"
                    >
                      {{ topic.trend === 'up' ? '📈 Trending' : '📉 Declining' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Chatbot in Split Screen Mode -->
        <div v-if="showSplitScreen" class="h-[calc(100vh-12rem)]">
          <ChatBotWrapper />
        </div>
      </div>
    </div>
    <!-- Floating Chat Bot (when not in split screen) -->
    <ChatBotWrapper v-if="!showSplitScreen" />
  </div>
</template>

<style scoped>
.material-icons {
  font-size: inherit;
  line-height: inherit;
  vertical-align: middle;
}

/* Smooth transitions */
.grid {
  transition: grid-template-columns 0.3s ease-in-out;
}

/* Improved scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
