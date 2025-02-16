<script>
import ChatBotWrapper from '@/components/ChatBotWrapper.vue'
import SideNavBar from '@/layouts/SideNavBar.vue'
import CourseEngagementChart from '@/views/faculty/components/CourseEngageChart.vue'
import GradeDistributionChart from '@/views/faculty/components/GradeDistributionChart.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
export default {
  name: 'FacultyDashboard',
  data() {
    return {
      queryEmpty: true,
      showSplitScreen: false,
      courses: ['Math', 'CT', 'SE', 'ST'],
      years: ['2025', '2024', '2023'],
      terms: ['Term 1', 'Term 2', 'Term 3'],
      selectedAggYear: '',
      selectedAggTerm: '',
      selectedCourse: '',
      selectedYear: '',
      selectedTerm: '',
      topics: [
        { id: 1, name: 'Machine Learning Basics', accessCount: 120, trend: 'up' },
        { id: 2, name: 'Data Structures', accessCount: 95, trend: 'down' },
        { id: 3, name: 'Deep Learning Fundamentals', accessCount: 78, trend: 'up' },
        { id: 4, name: 'Cloud Computing', accessCount: 60, trend: 'down' },
        { id: 5, name: 'Cybersecurity Essentials', accessCount: 130, trend: 'up' },
        { id: 6, name: 'Operating Systems', accessCount: 88, trend: 'down' },
      ],
      courseEngagement: {
        year: '2025',
        term: 'Term 1',
        data: [
          { name: 'Math', students: 100 },
          { name: 'CT', students: 95 },
          { name: 'SE', students: 80 },
          // { name: 'SE', students: 80 },
          { name: 'ST', students: 110 },
        ],
      },
      barXAxisLabel: 'Courses',
      barYAxisLabel: 'Number of Students',
      barChartTitle: 'Number of Students engaged in each course',
      gradeData: {
        Math: { S: 50, A: 100, B: 75, C: 40, D: 20, Fail: 15 },
        Software: { S: 40, A: 30, B: 85, C: 40, D: 20, Fail: 15 },
        Python: { S: 120, A: 30, B: 65, C: 40, D: 20, Fail: 15 },
        Java: { S: 25, A: 65, B: 89, C: 40, D: 5, Fail: 21 },
      },
      pieAxisLabel: 'Number of Students',
      pieChartTitle: 'Subjectwise Grade Distribution in the Term',
      showAlert: false,
      alertMessage: '',
      alertType: '',
    }
  },
  components: {
    ChatBotWrapper,
    SideNavBar,
    CourseEngagementChart,
    GradeDistributionChart,
    AlertMessage,
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
    triggerAlert(message, type) {
      this.alertMessage = message
      this.alertType = type
      this.showAlert = true

      setTimeout(() => {
        this.showAlert = false
      }, 3000) // Hide alert after 3 seconds
    },
    getAggregatedInsightsData() {
      //make api call with faculty, year and term data
      console.log('calling api to fetch data')
    },
    getFrequentlyAccessedTopicData() {
      console.log('calling api to fetch data')
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
        <div class="space-y-4 mx-auto">
          <!-- Aggregated graphical insights -->
          <div class="px-2 sm:px-4 py-2 border rounded-lg bg-white">
            <div class="px-2 sm:px-4 py-2">
              <div class="flex flex-col sm:flex-row gap-4 mb-4 justify-between">
                <!-- Heading -->
                <h1 class="text-2xl font-semibold text-gray-700">Aggregated Insights</h1>
                <!-- Filters Section -->
                <div class="flex flex-wrap gap-2">
                  <select v-model="selectedAggYear" class="px-4 py-2 bg-red-700 text-white rounded">
                    <option disabled value="">Year</option>
                    <option v-for="year in years" :key="year">{{ year }}</option>
                  </select>
                  <select
                    @change="getAggregatedInsightsData"
                    :disabled="selectedAggYear === ''"
                    v-model="selectedAggTerm"
                    class="px-4 py-2 bg-red-700 text-white rounded"
                  >
                    <option disabled value="">Term</option>
                    <option v-for="term in terms" :key="term">{{ term }}</option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <CourseEngagementChart
                    :courseData="courseEngagement['data']"
                    :xlabel="barXAxisLabel"
                    :ylabel="barYAxisLabel"
                    :chartTitle="barChartTitle"
                  />
                </div>
                <div>
                  <GradeDistributionChart
                    :gradeData="gradeData"
                    :xlabel="pieAxisLabel"
                    :pieChartTitle="pieChartTitle"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Frequently Accessed Topics insights -->
          <div class="px-2 sm:px-4 py-2 border rounded-lg bg-white">
            <div class="px-2 sm:px-4 py-2">
              <div class="flex flex-col sm:flex-row gap-4 mb-4 justify-between">
                <!-- Heading -->
                <h1 class="text-2xl font-semibold text-gray-700">Frequently Accessed Topics</h1>
                <!-- Filters Section -->
                <div class="flex flex-wrap gap-2">
                  <select v-model="selectedCourse" class="px-4 py-2 bg-red-700 text-white rounded">
                    <option disabled value="">Course</option>
                    <option v-for="course in courses" :key="course">{{ course }}</option>
                  </select>
                  <select
                    :disabled="selectedCourse === ''"
                    v-model="selectedYear"
                    class="px-4 py-2 bg-red-700 text-white rounded"
                  >
                    <option disabled value="">Year</option>
                    <option v-for="year in years" :key="year">{{ year }}</option>
                  </select>
                  <select
                    @change="getFrequentlyAccessedTopicData"
                    :disabled="selectedYear === ''"
                    v-model="selectedTerm"
                    class="px-4 py-2 bg-red-700 text-white rounded"
                  >
                    <option disabled value="">Term</option>
                    <option v-for="term in terms" :key="term">{{ term }}</option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                <div
                  v-for="topic in topics"
                  :key="topic.id"
                  class="p-4 bg-white rounded-lg shadow-md border border-gray-200 transition-transform transform hover:scale-105 hover:border-maroon-600"
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
