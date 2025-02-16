<script>
import { ref, onMounted } from 'vue'
import ChatBotWrapper from '@/components/ChatBotWrapper.vue'
import SideNavBar from '@/layouts/SideNavBar.vue'
import AnalyticsViewer from '@/components/faculty/AnalyticsViewer.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'

export default {
  name: 'FacultyDashboard',
  components: {
    ChatBotWrapper,
    SideNavBar,
    AnalyticsViewer,
    AlertMessage,
  },
  setup() {
    const showSplitScreen = ref(false)
    const showAlert = ref(false)
    const alertMessage = ref('')
    const alertType = ref('')
    const analyticsFilters = ref({
      course: '',
      year: '',
      term: ''
    })

    const courses = ['Math', 'CT', 'SE', 'ST']
    const years = ['2025', '2024', '2023']
    const terms = ['Term 1', 'Term 2', 'Term 3']

    const triggerAlert = (message, type) => {
      alertMessage.value = message
      alertType.value = type
      showAlert.value = true

      setTimeout(() => {
        showAlert.value = false
      }, 3000)
    }

    const updateFilters = () => {
      if (!analyticsFilters.value.course || !analyticsFilters.value.year || !analyticsFilters.value.term) {
        triggerAlert('Please select all filter values', 'warning')
        return
      }
      
      // Show success message when all filters are selected
      triggerAlert('Analytics data updated successfully', 'success')
    }

    // Set default values for demonstration
    onMounted(() => {
      analyticsFilters.value = {
        course: 'SE',
        year: '2024',
        term: 'Term 1'
      }
      updateFilters()
    })

    return {
      showSplitScreen,
      showAlert,
      alertMessage,
      alertType,
      analyticsFilters,
      courses,
      years,
      terms,
      triggerAlert,
      updateFilters
    }
  }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <div>
      <SideNavBar />
    </div>
    
    <div class="flex-1 overflow-y-auto">
      <div class="p-6 space-y-6">
        <!-- Alert Message -->
        <AlertMessage
          v-if="showAlert"
          :message="alertMessage"
          :type="alertType"
          class="fixed top-4 right-4 z-50"
        />

        <!-- Main Content -->
        <div class="grid" :class="{ 'md:grid-cols-3': showSplitScreen }" gap-6>
          <div :class="{ 'col-span-2': showSplitScreen }">
            <!-- Course Filters -->
            <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
              <div class="flex flex-wrap gap-4 items-center">
                <h3 class="text-lg font-semibold text-gray-800 mr-4">Course Filters</h3>
                
                <select
                  v-model="analyticsFilters.course"
                  class="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
                >
                  <option value="" disabled>Select Course</option>
                  <option v-for="course in courses" :key="course" :value="course">
                    {{ course }}
                  </option>
                </select>

                <select
                  v-model="analyticsFilters.year"
                  class="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
                >
                  <option value="" disabled>Select Year</option>
                  <option v-for="year in years" :key="year" :value="year">
                    {{ year }}
                  </option>
                </select>

                <select
                  v-model="analyticsFilters.term"
                  class="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
                  @change="updateFilters"
                >
                  <option value="" disabled>Select Term</option>
                  <option v-for="term in terms" :key="term" :value="term">
                    {{ term }}
                  </option>
                </select>

                <button
                  @click="updateFilters"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Update Analytics
                </button>
              </div>
            </div>

            <!-- Analytics Viewer -->
            <AnalyticsViewer :filters="analyticsFilters" />
          </div>

          <!-- AI Chatbot -->
          <div v-if="showSplitScreen" class="h-[calc(100vh-2rem)]">
            <ChatBotWrapper />
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Chat Bot Toggle -->
    <button
      @click="showSplitScreen = !showSplitScreen"
      class="fixed bottom-6 right-6 bg-red-600 text-white p-3 rounded-full shadow-lg hover:bg-red-700 transition-colors z-50"
    >
      <svg
        class="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          v-if="showSplitScreen"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
        <path
          v-else
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
        />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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
