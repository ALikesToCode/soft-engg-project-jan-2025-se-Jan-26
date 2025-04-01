<template>
  <!-- Only show content when not loading -->
  <div v-if="!isLoading">
    <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
      <template #role-content>
        <div class="space-y-6">
          <!-- Performance Overview -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-blue-50 rounded-lg">
                  <span class="material-icons text-blue-600">support_agent</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.ticketsResolved }}</div>
                  <div class="text-sm text-gray-600">Tickets Resolved</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">trending_up</span>
                  +12% this week
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-green-50 rounded-lg">
                  <span class="material-icons text-green-600">speed</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.responseTime }}h</div>
                  <div class="text-sm text-gray-600">Avg. Response Time</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">arrow_downward</span>
                  -30min improvement
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-purple-50 rounded-lg">
                  <span class="material-icons text-purple-600">thumb_up</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.satisfactionRate }}%</div>
                  <div class="text-sm text-gray-600">Satisfaction Rate</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">trending_up</span>
                  +2% this month
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-yellow-50 rounded-lg">
                  <span class="material-icons text-yellow-600">pending_actions</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.pendingTickets }}</div>
                  <div class="text-sm text-gray-600">Pending Tickets</div>
                </div>
              </div>
              <div class="mt-2">
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div class="bg-yellow-500 h-1.5 rounded-full" :style="{ width: pendingTicketsPercentage + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Current Tasks & Recent Activity -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Current Tasks -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">Current Tasks</h3>
                <button class="text-maroon-600 hover:text-maroon-700 text-sm font-medium">
                  View All
                </button>
              </div>
              <div class="space-y-4">
                <div v-for="task in currentTasks" :key="task.id" 
                     class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div class="flex items-start space-x-3">
                    <span class="material-icons text-maroon-600" :class="task.iconClass">{{ task.icon }}</span>
                    <div>
                      <div class="font-medium text-gray-900">{{ task.title }}</div>
                      <div class="text-sm text-gray-600">{{ task.description }}</div>
                    </div>
                  </div>
                  <span :class="['px-2 py-1 text-xs font-medium rounded-full', task.statusClass]">
                    {{ task.status }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">Recent Activity</h3>
                <div class="flex items-center space-x-2">
                  <button 
                    v-for="filter in activityFilters" 
                    :key="filter.value"
                    @click="currentActivityFilter = filter.value"
                    :class="[
                      'px-3 py-1 text-sm rounded-full transition-colors',
                      currentActivityFilter === filter.value
                        ? 'bg-maroon-100 text-maroon-800'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    ]"
                  >
                    {{ filter.label }}
                  </button>
                </div>
              </div>
              <div class="space-y-4">
                <div v-for="activity in filteredActivities" :key="activity.id" 
                     class="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                  <span class="material-icons text-maroon-600">{{ activity.icon }}</span>
                  <div>
                    <div class="font-medium text-gray-900">{{ activity.title }}</div>
                    <div class="text-sm text-gray-600">{{ activity.description }}</div>
                    <div class="text-xs text-gray-500 mt-1">{{ activity.timestamp }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Support Areas & Skills -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Areas of Support -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 class="text-xl font-semibold text-gray-800 mb-4">Areas of Support</h3>
              <div class="space-y-3">
                <div v-for="area in supportAreas" :key="area.name" class="flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span class="material-icons text-maroon-600">{{ area.icon }}</span>
                    <span class="text-gray-700">{{ area.name }}</span>
                  </div>
                  <div class="w-24">
                    <div class="w-full bg-gray-100 rounded-full h-1.5">
                      <div class="bg-maroon-600 h-1.5 rounded-full" :style="{ width: area.percentage + '%' }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Skills & Certifications -->
            <div class="col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 class="text-xl font-semibold text-gray-800 mb-4">Skills & Certifications</h3>
              <div class="flex flex-wrap gap-2">
                <span v-for="skill in skills" :key="skill.name"
                      class="px-3 py-1 rounded-full text-sm font-medium"
                      :class="skill.class">
                  {{ skill.name }}
                </span>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-100">
                <div class="grid grid-cols-2 gap-4">
                  <div v-for="cert in certifications" :key="cert.name" 
                       class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <span class="material-icons text-maroon-600">verified</span>
                    <div>
                      <div class="font-medium text-gray-900">{{ cert.name }}</div>
                      <div class="text-xs text-gray-500">{{ cert.date }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </BaseProfilePage>
  </div>
  
  <!-- Loading Overlay -->
  <div v-if="isLoading" class="fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50">
    <div class="text-center">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-maroon-600 border-t-transparent"></div>
      <p class="mt-4 text-lg font-medium text-gray-700">Loading your profile...</p>
    </div>
  </div>
</template>

<script>
import BaseProfilePage from '../base/BaseProfilePage.vue'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'

// Fallback avatar
const dummyAvatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=="

export default {
  name: 'SupportProfilePage',
  components: {
    BaseProfilePage
  },
  data() {
    return {
      userType: 'support',
      isLoading: true,
      currentActivityFilter: 'all',
      userInfo: {
        id: null,
        name: null,
        email: null,
        profilePictureUrl: dummyAvatar,
        coursesCount: 0,
        studentsCount: 0,
        rating: 0
      },
      stats: {
        ticketsResolved: 245,
        responseTime: 1.5,
        satisfactionRate: 98,
        pendingTickets: 12
      },
      activityFilters: [
        { label: 'All', value: 'all' },
        { label: 'Tickets', value: 'tickets' },
        { label: 'System', value: 'system' }
      ],
      recentActivities: [
        {
          id: 1,
          icon: 'check_circle',
          title: 'Resolved Technical Issue',
          description: 'Fixed login authentication problem for CS101 students',
          timestamp: '2 hours ago',
          type: 'tickets'
        },
        {
          id: 2,
          icon: 'campaign',
          title: 'System Notification Sent',
          description: 'Maintenance schedule announcement for weekend update',
          timestamp: '5 hours ago',
          type: 'system'
        },
        {
          id: 3,
          icon: 'people',
          title: 'Student Support',
          description: 'Assisted with course enrollment process',
          timestamp: '1 day ago',
          type: 'tickets'
        }
      ],
      currentTasks: [
        {
          id: 1,
          icon: 'priority_high',
          iconClass: 'text-red-600',
          title: 'Server Performance Issue',
          description: 'Investigating slow response times in the assignment submission system',
          status: 'High Priority',
          statusClass: 'bg-red-100 text-red-800'
        },
        {
          id: 2,
          icon: 'schedule',
          iconClass: 'text-yellow-600',
          title: 'Maintenance Planning',
          description: 'Preparing documentation for weekend system updates',
          status: 'In Progress',
          statusClass: 'bg-yellow-100 text-yellow-800'
        },
        {
          id: 3,
          icon: 'help',
          iconClass: 'text-blue-600',
          title: 'Student Inquiries',
          description: 'Responding to course access requests',
          status: 'Ongoing',
          statusClass: 'bg-blue-100 text-blue-800'
        }
      ],
      supportAreas: [
        { name: 'Technical Support', icon: 'computer', percentage: 95 },
        { name: 'Course Management', icon: 'school', percentage: 85 },
        { name: 'User Administration', icon: 'manage_accounts', percentage: 90 },
        { name: 'System Maintenance', icon: 'build', percentage: 88 }
      ],
      skills: [
        { name: 'Technical Troubleshooting', class: 'bg-blue-100 text-blue-800' },
        { name: 'User Training', class: 'bg-green-100 text-green-800' },
        { name: 'System Administration', class: 'bg-purple-100 text-purple-800' },
        { name: 'Documentation', class: 'bg-yellow-100 text-yellow-800' },
        { name: 'Course Platform', class: 'bg-maroon-100 text-maroon-800' }
      ],
      certifications: [
        { name: 'IT Support Professional', date: 'Achieved Jan 2024' },
        { name: 'Learning Platform Expert', date: 'Achieved Dec 2023' },
        { name: 'System Security Specialist', date: 'Achieved Nov 2023' },
        { name: 'Customer Service Excellence', date: 'Achieved Oct 2023' }
      ]
    }
  },
  computed: {
    pendingTicketsPercentage() {
      const maxTickets = 50 // Maximum expected pending tickets
      return (this.stats.pendingTickets / maxTickets) * 100
    },
    filteredActivities() {
      if (this.currentActivityFilter === 'all') return this.recentActivities
      return this.recentActivities.filter(activity => activity.type === this.currentActivityFilter)
    }
  },
  mounted() {
    this.loadUserProfile()
  },
  methods: {
    showSuccessToast(msg) {
      const toast = useToast()
      toast.success(msg, { timeout: 3000 })
    },
    showErrorToast(error, defaultMessage) {
      const toast = useToast()
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    },
    async loadUserProfile() {
      this.isLoading = true
      try {
        // Get token once
        const token = localStorage.getItem('token')
        if (!token) {
          throw new Error('No authentication token found')
        }
        
        const headers = {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }

        // Use the api utility with correct base URL
        const response = await api.get('/user/profile', headers)
        if (response.status !== 200) {
          throw new Error('Failed to fetch user profile data')
        }

        console.log('Profile data received:', response.data)

        // Update user information
        this.userInfo = {
          id: response.data.id,
          name: response.data.name,
          email: response.data.email,
          profilePictureUrl: response.data.profile_pic_url || dummyAvatar,
          coursesCount: response.data.courses_count || 0,
          studentsCount: response.data.students_count || 0,
          rating: response.data.rating || 5.0
        }
        
        this.showSuccessToast('Profile loaded successfully')
      } catch (error) {
        console.error('Error fetching user profile:', error)
        this.showErrorToast(error, 'Failed to load profile data')
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script> 