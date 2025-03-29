<!-- Academic Integrity Monitoring Component -->
<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Side Navigation - Fixed position -->
    <div class="fixed inset-y-0 left-0">
      <SideNavBar />
    </div>
    
    <!-- Main Content Area - Scrollable with margin for sidebar -->
    <div class="flex-1 ml-16 overflow-auto">
      <div class="p-6">
        <!-- Header Section -->
        <header class="mb-8">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Academic Integrity Monitoring</h1>
              <p class="mt-2 text-gray-600">Monitor and manage potential academic integrity concerns</p>
            </div>
            <div class="flex space-x-4">
              <!-- Filter Dropdown -->
              <select
                v-model="filters.severity"
                class="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">All Severities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <!-- Time Range Dropdown -->
              <select
                v-model="filters.timeRange"
                class="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="all">All Time</option>
              </select>
            </div>
          </div>
        </header>

        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-sm font-medium text-gray-500">Total Flags</h3>
            <p class="mt-2 text-3xl font-semibold text-gray-900">{{ statistics.totalFlags }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-sm font-medium text-gray-500">High Severity</h3>
            <p class="mt-2 text-3xl font-semibold text-red-600">{{ statistics.highSeverity }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-sm font-medium text-gray-500">Pending Review</h3>
            <p class="mt-2 text-3xl font-semibold text-yellow-600">{{ statistics.pendingReview }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-sm font-medium text-gray-500">Resolved</h3>
            <p class="mt-2 text-3xl font-semibold text-green-600">{{ statistics.resolved }}</p>
          </div>
        </div>

        <!-- LLM Validation Tools Section -->
        <div class="grid grid-cols-1 md:grid-cols-1 gap-6 mb-8">
          <!-- LLM Chat with Integrity Checking -->
          <LLMChatIntegrityCheck />
        </div>

        <!-- Flagged Items Table -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Flagged Interactions</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Course
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Severity
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="flag in paginatedFlags" :key="flag.id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(flag.timestamp) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{{ flag.studentName }}</div>
                    <div class="text-sm text-gray-500">{{ flag.studentId }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">{{ flag.courseName }}</div>
                    <div class="text-sm text-gray-500">{{ flag.courseCode }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="[
                        'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                        {
                          'bg-red-100 text-red-800': flag.severity === 'high',
                          'bg-yellow-100 text-yellow-800': flag.severity === 'medium',
                          'bg-green-100 text-green-800': flag.severity === 'low'
                        }
                      ]"
                    >
                      {{ flag.severity }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="[
                        'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full',
                        {
                          'bg-gray-100 text-gray-800': flag.status === 'pending',
                          'bg-green-100 text-green-800': flag.status === 'reviewed',
                          'bg-red-100 text-red-800': flag.status === 'escalated'
                        }
                      ]"
                    >
                      {{ flag.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      @click="openDetailsModal(flag)"
                      class="text-indigo-600 hover:text-indigo-900"
                    >
                      Details
                    </button>
                    <button
                      v-if="flag.status === 'pending'"
                      @click="markAsReviewed(flag)"
                      class="text-green-600 hover:text-green-900"
                    >
                      Mark Reviewed
                    </button>
                    <button
                      v-if="flag.status !== 'escalated'"
                      @click="openEscalateModal(flag)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Escalate
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="mt-4 flex items-center justify-between px-4">
              <button
                @click="currentPage > 1 && currentPage--"
                class="px-4 py-2 border rounded"
                :disabled="currentPage === 1"
              >
                Previous
              </button>
              <span>Page {{ currentPage }}</span>
              <button
                @click="currentPage < Math.ceil(flaggedItems.length / 10) && currentPage++"
                class="px-4 py-2 border rounded"
                :disabled="currentPage >= Math.ceil(flaggedItems.length / 10)"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div class="relative top-20 mx-auto p-5 border w-3/4 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">Flag Details</h3>
            <button @click="showDetailsModal = false" class="text-gray-400 hover:text-gray-500">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="space-y-4">
            <!-- Flag Details Content -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-2">Interaction Details</h4>
              <p class="text-gray-700">{{ selectedFlag?.details }}</p>
            </div>
            <!-- Audit Trail -->
            <div class="space-y-2">
              <h4 class="font-medium text-gray-900">Audit Trail</h4>
              <div v-for="(audit, index) in auditTrail" :key="index" class="bg-gray-50 p-3 rounded-lg">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-700">{{ audit.action }}</span>
                  <span class="text-gray-500">{{ formatDate(audit.timestamp) }}</span>
                </div>
                <p v-if="audit.comment" class="text-gray-600 mt-1 text-sm">{{ audit.comment }}</p>
              </div>
            </div>
            <!-- Add Comment -->
            <div>
              <label class="block text-sm font-medium text-gray-700">Add Comment</label>
              <textarea
                v-model="newComment"
                rows="3"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              ></textarea>
            </div>
            <div class="flex justify-end space-x-2">
              <button
                @click="showDetailsModal = false"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              <button
                @click="submitComment"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                Submit Comment
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Escalate Modal -->
    <div v-if="showEscalateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">Escalate Flag</h3>
            <button @click="showEscalateModal = false" class="text-gray-400 hover:text-gray-500">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <form @submit.prevent="submitEscalation" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Reason for Escalation</label>
              <textarea
                v-model="escalationDetails.reason"
                rows="3"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Escalation Level</label>
              <select
                v-model="escalationDetails.level"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                required
              >
                <option value="department">Department Level</option>
                <option value="faculty">Faculty Level</option>
                <option value="institution">Institution Level</option>
              </select>
            </div>
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                @click="showEscalateModal = false"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Escalate
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { AcademicIntegrityService } from '@/services/academicIntegrity.service'
import SideNavBar from '@/layouts/SideNavBar.vue'
import LLMChatIntegrityCheck from '@/components/LLMChatIntegrityCheck.vue'

export default {
  name: 'AcademicIntegrityMonitoring',
  components: {
    SideNavBar,
    LLMChatIntegrityCheck
  },
  setup() {
    // Mock Data
    const mockData = {
      flaggedInteractions: [
        {
          id: 1,
          timestamp: new Date('2024-01-25T10:30:00'),
          studentName: 'John Smith',
          studentId: 'STU001',
          courseName: 'Advanced Programming',
          courseCode: 'CS401',
          severity: 'high',
          status: 'pending',
          details: 'Multiple instances of code similarity detected with external sources during the final project submission.'
        },
        {
          id: 2,
          timestamp: new Date('2024-01-24T14:15:00'),
          studentName: 'Emma Johnson',
          studentId: 'STU002',
          courseName: 'Data Structures',
          courseCode: 'CS301',
          severity: 'medium',
          status: 'reviewed',
          details: 'Unusual pattern of quiz responses matching with another student.'
        },
        {
          id: 3,
          timestamp: new Date('2024-01-23T09:45:00'),
          studentName: 'Michael Brown',
          studentId: 'STU003',
          courseName: 'Software Engineering',
          courseCode: 'CS402',
          severity: 'low',
          status: 'escalated',
          details: 'Potential unauthorized collaboration during online assessment.'
        },
        {
          id: 4,
          timestamp: new Date('2024-01-22T16:20:00'),
          studentName: 'Sarah Wilson',
          studentId: 'STU004',
          courseName: 'Advanced Programming',
          courseCode: 'CS401',
          severity: 'high',
          status: 'pending',
          details: 'Suspicious browser activity detected during online exam.'
        },
        {
          id: 5,
          timestamp: new Date('2024-01-21T11:00:00'),
          studentName: 'David Lee',
          studentId: 'STU005',
          courseName: 'Data Structures',
          courseCode: 'CS301',
          severity: 'medium',
          status: 'pending',
          details: 'Multiple rapid tab switches detected during quiz attempt.'
        }
      ],
      statistics: {
        totalFlags: 27,
        highSeverity: 8,
        pendingReview: 12,
        resolved: 15
      },
      auditTrail: [
        {
          id: 1,
          flagId: 1,
          timestamp: new Date('2024-01-25T10:35:00'),
          action: 'Flag Created',
          comment: 'Initial detection by automated system'
        },
        {
          id: 2,
          flagId: 1,
          timestamp: new Date('2024-01-25T11:00:00'),
          action: 'Review Started',
          comment: 'Initial review by course instructor'
        },
        {
          id: 3,
          flagId: 1,
          timestamp: new Date('2024-01-25T14:20:00'),
          action: 'Evidence Added',
          comment: 'Added screenshots of matching code segments'
        }
      ]
    }

    // State
    const flaggedItems = ref([])
    const currentPage = ref(1)
    const itemsPerPage = 10
    const statistics = ref({
      totalFlags: 0,
      highSeverity: 0,
      pendingReview: 0,
      resolved: 0
    })
    const filters = ref({
      severity: '',
      timeRange: 'week'
    })
    const showDetailsModal = ref(false)
    const showEscalateModal = ref(false)
    const selectedFlag = ref(null)
    const auditTrail = ref([])
    const newComment = ref('')
    const escalationDetails = ref({
      reason: '',
      level: 'department'
    })

    // Computed
    const paginatedFlags = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return flaggedItems.value.slice(start, end)
    })

    // Methods
    const fetchFlaggedItems = async () => {
      try {
        // Simulate API call with mock data
        const filteredItems = mockData.flaggedInteractions.filter(item => {
          if (filters.value.severity && item.severity !== filters.value.severity) {
            return false
          }
          // Add time range filtering logic here if needed
          return true
        })
        flaggedItems.value = filteredItems
        currentPage.value = 1
      } catch (error) {
        console.error('Error fetching flagged items:', error)
        flaggedItems.value = []
      }
    }

    const fetchStatistics = async () => {
      try {
        // Use mock statistics
        statistics.value = mockData.statistics
      } catch (error) {
        console.error('Error fetching statistics:', error)
      }
    }

    const fetchAuditTrail = async (flagId) => {
      try {
        // Filter audit trail for specific flag
        auditTrail.value = mockData.auditTrail.filter(audit => audit.flagId === flagId)
      } catch (error) {
        console.error('Error fetching audit trail:', error)
      }
    }

    const openDetailsModal = async (flag) => {
      selectedFlag.value = flag
      await fetchAuditTrail(flag.id)
      showDetailsModal.value = true
    }

    const openEscalateModal = (flag) => {
      selectedFlag.value = flag
      showEscalateModal.value = true
    }

    const markAsReviewed = async (flag) => {
      try {
        // Update mock data
        const flagIndex = mockData.flaggedInteractions.findIndex(f => f.id === flag.id)
        if (flagIndex !== -1) {
          mockData.flaggedInteractions[flagIndex].status = 'reviewed'
          mockData.statistics.pendingReview--
          mockData.statistics.resolved++
        }
        await fetchFlaggedItems()
        await fetchStatistics()
      } catch (error) {
        console.error('Error marking flag as reviewed:', error)
      }
    }

    const submitComment = async () => {
      if (!newComment.value.trim()) return

      try {
        // Add comment to mock audit trail
        const newAudit = {
          id: mockData.auditTrail.length + 1,
          flagId: selectedFlag.value.id,
          timestamp: new Date(),
          action: 'Comment Added',
          comment: newComment.value
        }
        mockData.auditTrail.push(newAudit)
        await fetchAuditTrail(selectedFlag.value.id)
        newComment.value = ''
      } catch (error) {
        console.error('Error submitting comment:', error)
      }
    }

    const submitEscalation = async () => {
      try {
        // Update mock data
        const flagIndex = mockData.flaggedInteractions.findIndex(f => f.id === selectedFlag.value.id)
        if (flagIndex !== -1) {
          mockData.flaggedInteractions[flagIndex].status = 'escalated'
          // Add escalation to audit trail
          mockData.auditTrail.push({
            id: mockData.auditTrail.length + 1,
            flagId: selectedFlag.value.id,
            timestamp: new Date(),
            action: `Escalated to ${escalationDetails.value.level} level`,
            comment: escalationDetails.value.reason
          })
        }
        await fetchFlaggedItems()
        await fetchStatistics()
        showEscalateModal.value = false
        escalationDetails.value = {
          reason: '',
          level: 'department'
        }
      } catch (error) {
        console.error('Error escalating flag:', error)
      }
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      try {
        return new Date(date).toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return 'Invalid Date'
      }
    }

    // Watch for filter changes
    watch(filters, () => {
      fetchFlaggedItems()
    })

    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([
        fetchFlaggedItems(),
        fetchStatistics()
      ])
    })

    return {
      flaggedItems,
      statistics,
      filters,
      showDetailsModal,
      showEscalateModal,
      selectedFlag,
      auditTrail,
      newComment,
      escalationDetails,
      paginatedFlags,
      currentPage,
      openDetailsModal,
      openEscalateModal,
      markAsReviewed,
      submitComment,
      submitEscalation,
      formatDate
    }
  }
}
</script> 