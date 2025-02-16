<script>
import { ref, onMounted, watch } from 'vue'
// import { analyticsService } from '@/services/analyticsService'
import { mockAnalyticsService as analyticsService } from '@/services/mockAnalyticsData'
import { Line, Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement
)

export default {
  name: 'AnalyticsViewer',
  components: {
    Line,
    Bar,
    Doughnut
  },
  props: {
    filters: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const analyticsData = ref(null)
    const aiInsights = ref([])
    const isLoading = ref(false)
    const selectedDateRange = ref('last30days')
    const selectedMetric = ref('engagement')
    const error = ref(null)
    const retryCount = ref(0)
    const MAX_RETRIES = 3

    const dateRanges = [
      { value: 'last7days', label: 'Last 7 Days' },
      { value: 'last30days', label: 'Last 30 Days' },
      { value: 'last3months', label: 'Last 3 Months' },
      { value: 'lastYear', label: 'Last Year' }
    ]

    const metrics = [
      { value: 'engagement', label: 'Student Engagement' },
      { value: 'performance', label: 'Course Performance' },
      { value: 'resources', label: 'Resource Usage' }
    ]

    const clearError = () => {
      error.value = null
      retryCount.value = 0
    }

    const fetchAnalytics = async (shouldRetry = true) => {
      try {
        if (!props.filters.course || !props.filters.year || !props.filters.term) {
          error.value = 'Please select all course filters before fetching analytics'
          return
        }

        isLoading.value = true
        clearError()

        console.log('Fetching analytics with params:', {
          ...props.filters,
          dateRange: selectedDateRange.value,
          metric: selectedMetric.value
        })

        const data = await analyticsService.getFacultyAnalytics({
          ...props.filters,
          dateRange: selectedDateRange.value,
          metric: selectedMetric.value
        })

        if (!data || !data.kpis) {
          throw new Error('Invalid analytics data format received')
        }

        analyticsData.value = data
        await fetchAIInsights(data)
      } catch (err) {
        console.error('Analytics fetch error:', err)
        
        if (shouldRetry && retryCount.value < MAX_RETRIES) {
          retryCount.value++
          error.value = `Attempt ${retryCount.value}/${MAX_RETRIES}: Retrying...`
          setTimeout(() => fetchAnalytics(), 2000 * retryCount.value) // Exponential backoff
          return
        }

        error.value = err.message || 'Failed to fetch analytics data'
      } finally {
        isLoading.value = false
      }
    }

    const fetchAIInsights = async (data) => {
      try {
        if (!data) return
        
        const insights = await analyticsService.getAIInsights(data)
        if (Array.isArray(insights) && insights.length > 0) {
          aiInsights.value = insights
        } else {
          console.warn('No AI insights available')
          aiInsights.value = []
        }
      } catch (err) {
        console.error('Failed to fetch AI insights:', err)
        // Don't show error to user, just log it
        aiInsights.value = []
      }
    }

    const retryFetch = () => {
      clearError()
      fetchAnalytics(true)
    }

    const exportData = async (format) => {
      try {
        if (!analyticsData.value) {
          throw new Error('No data available to export')
        }

        isLoading.value = true
        clearError()

        const blob = await analyticsService.exportAnalytics(format, {
          ...props.filters,
          dateRange: selectedDateRange.value,
          metric: selectedMetric.value
        })
        
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `analytics-report-${new Date().toISOString()}.${format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (err) {
        error.value = `Failed to export data: ${err.message}`
        console.error('Export error:', err)
      } finally {
        isLoading.value = false
      }
    }

    // Watch for changes in filters or settings
    watch(
      [
        () => props.filters,
        selectedDateRange,
        selectedMetric
      ],
      () => {
        if (props.filters.course && props.filters.year && props.filters.term) {
          fetchAnalytics(true)
        }
      },
      { deep: true }
    )

    onMounted(() => {
      if (props.filters.course && props.filters.year && props.filters.term) {
        fetchAnalytics(true)
      }
    })

    return {
      analyticsData,
      aiInsights,
      isLoading,
      error,
      selectedDateRange,
      selectedMetric,
      dateRanges,
      metrics,
      exportData,
      retryFetch,
      retryCount,
      MAX_RETRIES
    }
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <!-- Header Section -->
    <div class="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
      <div>
        <h2 class="text-2xl font-semibold text-gray-900">Analytics Dashboard</h2>
        <p class="text-gray-700 mt-1">Comprehensive course performance and engagement metrics</p>
      </div>
      
      <div class="flex flex-wrap gap-4">
        <!-- Filters -->
        <select
          v-model="selectedDateRange"
          class="px-4 py-2 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
        >
          <option v-for="range in dateRanges" :key="range.value" :value="range.value">
            {{ range.label }}
          </option>
        </select>

        <!-- Export Buttons -->
        <div class="flex gap-2">
          <button
            @click="exportData('pdf')"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
            :disabled="isLoading"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export PDF
          </button>
          <button
            @click="exportData('csv')"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
            :disabled="isLoading"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export CSV
          </button>
        </div>
      </div>
    </div>

    <!-- Loading and Error States -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="flex flex-col items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-700 mb-4"></div>
        <p class="text-gray-600">{{ error || 'Loading analytics...' }}</p>
      </div>
    </div>

    <div v-else-if="error" class="bg-red-50 p-6 rounded-lg mb-6">
      <div class="flex flex-col items-center text-center">
        <svg class="w-12 h-12 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 class="text-lg font-semibold text-red-700 mb-2">{{ error }}</h3>
        <p class="text-red-600 mb-4">Please check your connection and try again</p>
        <button
          @click="retryFetch"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          :disabled="isLoading"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Analytics Content -->
    <div v-else-if="analyticsData" class="space-y-8">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="(kpi, index) in analyticsData.kpis"
          :key="index"
          class="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-gray-900">{{ kpi.label }}</h3>
            <span :class="kpi.trend > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 rounded-full text-xs font-semibold">
              {{ kpi.trend > 0 ? '↑' : '↓' }} {{ Math.abs(kpi.trend) }}%
            </span>
          </div>
          <div class="text-3xl font-bold text-gray-900">{{ kpi.value }}</div>
          <p class="text-sm text-gray-700 mt-1">{{ kpi.subtext }}</p>
        </div>
      </div>

      <!-- Main Analytics Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Course Enrollment Chart -->
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Course Enrollment</h3>
          <div class="h-80">
            <Bar
              v-if="analyticsData.courseEnrollmentData"
              :data="analyticsData.courseEnrollmentData"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Number of Students',
                      color: '#111827'
                    },
                    ticks: {
                      color: '#374151'
                    }
                  },
                  x: {
                    ticks: {
                      color: '#374151'
                    }
                  }
                }
              }"
            />
          </div>
        </div>

        <!-- Grade Distribution Chart -->
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Grade Distribution</h3>
          <div class="h-80">
            <Doughnut
              v-if="analyticsData.gradeDistributionData"
              :data="analyticsData.gradeDistributionData"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'right',
                    labels: {
                      color: '#374151',
                      font: {
                        weight: 500
                      }
                    }
                  }
                }
              }"
            />
          </div>
        </div>

        <!-- Performance Metrics -->
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Performance Trends</h3>
          <div class="h-80">
            <Line
              v-if="analyticsData.performanceMetrics"
              :data="analyticsData.performanceMetrics"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                    labels: {
                      color: '#374151',
                      font: {
                        weight: 500
                      }
                    }
                  }
                },
                scales: {
                  y: {
                    min: 0,
                    max: 100,
                    ticks: {
                      color: '#374151'
                    }
                  },
                  x: {
                    ticks: {
                      color: '#374151'
                    }
                  }
                }
              }"
            />
          </div>
        </div>

        <!-- Student Engagement Patterns -->
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Daily Engagement Pattern</h3>
          <div class="h-80">
            <Bar
              v-if="analyticsData.engagementPatterns"
              :data="analyticsData.engagementPatterns"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Active Hours',
                      color: '#111827'
                    },
                    ticks: {
                      color: '#374151'
                    }
                  },
                  x: {
                    ticks: {
                      color: '#374151'
                    }
                  }
                }
              }"
            />
          </div>
        </div>

        <!-- Resource Utilization -->
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Resource Utilization</h3>
          <div class="h-80">
            <Doughnut
              v-if="analyticsData.resourceUtilization"
              :data="analyticsData.resourceUtilization"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'right',
                    labels: {
                      color: '#374151',
                      font: {
                        weight: 500
                      }
                    }
                  }
                }
              }"
            />
          </div>
        </div>

        <!-- Frequently Accessed Topics -->
        <div class="bg-white p-6 rounded-lg border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Topic Analytics</h3>
          <div class="space-y-4 max-h-80 overflow-y-auto">
            <div
              v-for="topic in analyticsData.topicAccessData"
              :key="topic.id"
              class="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h4 class="font-medium text-gray-900">{{ topic.name }}</h4>
                  <p class="text-sm text-gray-700">{{ topic.accessCount }} accesses</p>
                </div>
                <span
                  :class="topic.trend === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-3 py-1 rounded-full text-sm font-medium"
                >
                  {{ topic.trend === 'up' ? '↑ Trending' : '↓ Declining' }}
                </span>
              </div>
              <div class="grid grid-cols-3 gap-4 mt-2">
                <div class="text-sm">
                  <span class="text-gray-700 font-medium">Avg Time:</span>
                  <span class="text-gray-900 ml-1">{{ topic.avgTimeSpent }}</span>
                </div>
                <div class="text-sm">
                  <span class="text-gray-700 font-medium">Completion:</span>
                  <span class="text-gray-900 ml-1">{{ topic.completionRate }}</span>
                </div>
                <div class="text-sm">
                  <span class="text-gray-700 font-medium">Difficulty:</span>
                  <span class="text-gray-900 ml-1">{{ topic.difficulty }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Insights Section -->
      <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">AI-Enhanced Insights</h3>
          <span class="text-sm text-gray-700">Updated {{ new Date().toLocaleDateString() }}</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(insight, index) in aiInsights"
            :key="index"
            class="flex items-start gap-4 p-4 bg-white rounded-lg shadow-sm"
          >
            <div :class="{
              'text-yellow-600': insight.severity === 'medium',
              'text-red-600': insight.severity === 'high',
              'text-green-600': insight.severity === 'low'
            }">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2 mb-2">
                <h4 class="font-medium text-gray-900">{{ insight.title }}</h4>
                <span :class="{
                  'bg-yellow-100 text-yellow-800': insight.severity === 'medium',
                  'bg-red-100 text-red-800': insight.severity === 'high',
                  'bg-green-100 text-green-800': insight.severity === 'low'
                }" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ insight.severity }}
                </span>
              </div>
              <p class="text-gray-700 mb-2">{{ insight.description }}</p>
              <div class="text-sm font-medium text-gray-900 mt-2">
                Recommendation:
                <span class="text-gray-700 font-normal">{{ insight.recommendation }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Data State -->
    <div v-else class="text-center text-gray-600 py-12">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-lg">No analytics data available</p>
      <p class="text-sm text-gray-500 mt-2">Please select different filters or try again later</p>
    </div>
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

/* Enhanced scrollbar styling */
.max-h-80::-webkit-scrollbar {
  width: 6px;
}

.max-h-80::-webkit-scrollbar-track {
  background: #F3F4F6;
  border-radius: 3px;
}

.max-h-80::-webkit-scrollbar-thumb {
  background-color: #94A3B8;
  border-radius: 3px;
}

.max-h-80::-webkit-scrollbar-thumb:hover {
  background-color: #64748B;
}
</style> 