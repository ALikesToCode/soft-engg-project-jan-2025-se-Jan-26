<template>
  <!-- Only show content when not loading -->
  <div v-if="!isLoading">
    <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
      <template #role-content>
        <div class="space-y-6">
          <!-- System Overview -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-blue-50 rounded-lg">
                  <span class="material-icons text-blue-600">people</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.totalUsers }}</div>
                  <div class="text-sm text-gray-600">Active Users</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">trending_up</span>
                  +{{ stats.newUsers }} this week
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-green-50 rounded-lg">
                  <span class="material-icons text-green-600">school</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.totalCourses }}</div>
                  <div class="text-sm text-gray-600">Total Courses</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">add_circle</span>
                  +{{ stats.newCourses }} new
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-purple-50 rounded-lg">
                  <span class="material-icons text-purple-600">warning</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.activeIssues }}</div>
                  <div class="text-sm text-gray-600">Active Issues</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span :class="stats.issueChange > 0 ? 'text-red-600' : 'text-green-600'" class="flex items-center">
                  <span class="material-icons text-sm mr-1">{{ stats.issueChange > 0 ? 'trending_up' : 'trending_down' }}</span>
                  {{ stats.issueChange > 0 ? '+' : '' }}{{ stats.issueChange }}% this week
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-yellow-50 rounded-lg">
                  <span class="material-icons text-yellow-600">speed</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.serverLoad }}%</div>
                  <div class="text-sm text-gray-600">Server Load</div>
                </div>
              </div>
              <div class="mt-2">
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div :class="stats.serverLoad < 70 ? 'bg-green-500' : stats.serverLoad < 90 ? 'bg-yellow-500' : 'bg-red-500'" 
                       class="h-1.5 rounded-full" 
                       :style="{ width: stats.serverLoad + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Admin Dashboard & User Activity -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- User Distribution -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 class="text-xl font-semibold text-gray-800 mb-4">User Distribution</h3>
              <div class="space-y-4">
                <div v-for="role in userDistribution" :key="role.name" class="flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span class="material-icons" :class="role.iconColor">{{ role.icon }}</span>
                    <span class="text-gray-700">{{ role.name }}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-gray-900 font-medium">{{ role.count }}</span>
                    <span class="text-xs px-2 py-1 rounded-full" :class="role.bgColor">{{ role.percentage }}%</span>
                  </div>
                </div>
              </div>
              <div class="mt-4 pt-4 border-t border-gray-100">
                <div class="h-12 w-full flex rounded-lg overflow-hidden">
                  <div v-for="role in userDistribution" :key="role.name" 
                      :style="{ width: role.percentage + '%' }" 
                      :class="role.barColor"></div>
                </div>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">System Activity</h3>
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
                  <div :class="['p-2 rounded-lg', activity.iconBg]">
                    <span class="material-icons text-white">{{ activity.icon }}</span>
                  </div>
                  <div class="flex-grow">
                    <div class="flex items-start justify-between">
                      <div>
                        <div class="font-medium text-gray-900">{{ activity.title }}</div>
                        <div class="text-sm text-gray-600">{{ activity.description }}</div>
                      </div>
                      <div class="text-xs text-gray-500">{{ activity.timestamp }}</div>
                    </div>
                    <div v-if="activity.actionable" class="mt-2">
                      <button class="px-3 py-1 bg-maroon-600 text-white text-xs font-medium rounded-lg hover:bg-maroon-700 transition-colors">
                        Review
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- System Health & Pending Actions -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- System Health -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 class="text-xl font-semibold text-gray-800 mb-4">System Health</h3>
              <div class="space-y-4">
                <div v-for="service in systemServices" :key="service.name" 
                    class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div class="flex items-center space-x-3">
                    <div :class="['p-2 rounded-lg', service.status === 'Operational' ? 'bg-green-500' : service.status === 'Warning' ? 'bg-yellow-500' : 'bg-red-500']">
                      <span class="material-icons text-white">{{ service.icon }}</span>
                    </div>
                    <div>
                      <div class="font-medium text-gray-900">{{ service.name }}</div>
                      <div class="text-xs text-gray-600">{{ service.lastChecked }}</div>
                    </div>
                  </div>
                  <span :class="['px-2 py-1 text-xs font-medium rounded-full', 
                    service.status === 'Operational' ? 'bg-green-100 text-green-800' : 
                    service.status === 'Warning' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-red-100 text-red-800']">
                    {{ service.status }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Pending Actions -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 class="text-xl font-semibold text-gray-800 mb-4">Pending Approvals</h3>
              <div class="space-y-4">
                <div v-for="action in pendingActions" :key="action.id" 
                    class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div class="flex items-start space-x-3">
                    <span class="material-icons text-maroon-600">{{ action.icon }}</span>
                    <div>
                      <div class="font-medium text-gray-900">{{ action.title }}</div>
                      <div class="text-xs text-gray-600">{{ action.requestedBy }} • {{ action.requestedAt }}</div>
                    </div>
                  </div>
                  <div class="flex space-x-2">
                    <button class="px-3 py-1 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 transition-colors">
                      Approve
                    </button>
                    <button class="px-3 py-1 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 transition-colors">
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Admin Tools -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">Admin Tools</h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
              <div v-for="tool in adminTools" :key="tool.name" 
                   class="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <div :class="['p-3 rounded-full mb-2', tool.bgColor]">
                  <span class="material-icons text-white">{{ tool.icon }}</span>
                </div>
                <div class="text-sm font-medium text-gray-900 text-center">{{ tool.name }}</div>
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
  name: 'AdminProfilePage',
  components: {
    BaseProfilePage
  },
  data() {
    return {
      userType: 'admin',
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
        totalUsers: 1245,
        newUsers: 87,
        totalCourses: 78,
        newCourses: 4,
        activeIssues: 12,
        issueChange: -8,
        serverLoad: 68
      },
      userDistribution: [
        {
          name: 'Students',
          count: 983,
          percentage: 78,
          icon: 'school',
          iconColor: 'text-blue-600',
          bgColor: 'bg-blue-100 text-blue-800',
          barColor: 'bg-blue-500'
        },
        {
          name: 'Instructors',
          count: 187,
          percentage: 15,
          icon: 'person',
          iconColor: 'text-green-600',
          bgColor: 'bg-green-100 text-green-800',
          barColor: 'bg-green-500'
        },
        {
          name: 'Support',
          count: 56,
          percentage: 5,
          icon: 'support_agent',
          iconColor: 'text-purple-600',
          bgColor: 'bg-purple-100 text-purple-800',
          barColor: 'bg-purple-500'
        },
        {
          name: 'Admins',
          count: 19,
          percentage: 2,
          icon: 'admin_panel_settings',
          iconColor: 'text-maroon-600',
          bgColor: 'bg-maroon-100 text-maroon-800',
          barColor: 'bg-maroon-600'
        }
      ],
      activityFilters: [
        { label: 'All', value: 'all' },
        { label: 'System', value: 'system' },
        { label: 'User', value: 'user' }
      ],
      recentActivities: [
        {
          id: 1,
          icon: 'warning',
          iconBg: 'bg-red-600',
          title: 'Database Performance Issue',
          description: 'High query latency detected in student records database',
          timestamp: '35 minutes ago',
          type: 'system',
          actionable: true
        },
        {
          id: 2,
          icon: 'person_add',
          iconBg: 'bg-green-600',
          title: 'New Instructor Onboarded',
          description: 'Dr. James Wilson added as Data Science instructor',
          timestamp: '2 hours ago',
          type: 'user',
          actionable: false
        },
        {
          id: 3,
          icon: 'update',
          iconBg: 'bg-blue-600',
          title: 'System Update Completed',
          description: 'Assignment submission module updated to version 2.4',
          timestamp: '5 hours ago',
          type: 'system',
          actionable: false
        },
        {
          id: 4,
          icon: 'security',
          iconBg: 'bg-yellow-600',
          title: 'Security Audit',
          description: 'Weekly security scan completed with 2 warnings',
          timestamp: '1 day ago',
          type: 'system',
          actionable: true
        }
      ],
      systemServices: [
        {
          name: 'Application Server',
          status: 'Operational',
          lastChecked: 'Last checked 5 minutes ago',
          icon: 'dns'
        },
        {
          name: 'Database Server',
          status: 'Warning',
          lastChecked: 'Last checked 5 minutes ago',
          icon: 'storage'
        },
        {
          name: 'Authentication Service',
          status: 'Operational',
          lastChecked: 'Last checked 5 minutes ago',
          icon: 'security'
        },
        {
          name: 'Storage Service',
          status: 'Operational',
          lastChecked: 'Last checked 5 minutes ago',
          icon: 'cloud'
        }
      ],
      pendingActions: [
        {
          id: 1,
          icon: 'person_add',
          title: 'New Instructor Approval',
          requestedBy: 'HR Department',
          requestedAt: '2 hours ago'
        },
        {
          id: 2,
          icon: 'school',
          title: 'New Course Approval',
          requestedBy: 'Dr. Sarah Chen',
          requestedAt: '5 hours ago'
        },
        {
          id: 3,
          icon: 'content_copy',
          title: 'Content Policy Exception',
          requestedBy: 'Prof. Robert Thomas',
          requestedAt: '1 day ago'
        }
      ],
      adminTools: [
        {
          name: 'User Management',
          icon: 'manage_accounts',
          bgColor: 'bg-blue-600'
        },
        {
          name: 'System Settings',
          icon: 'settings',
          bgColor: 'bg-gray-700'
        },
        {
          name: 'Course Management',
          icon: 'book',
          bgColor: 'bg-green-600'
        },
        {
          name: 'Reports',
          icon: 'bar_chart',
          bgColor: 'bg-maroon-600'
        },
        {
          name: 'Audit Logs',
          icon: 'receipt_long',
          bgColor: 'bg-purple-600'
        }
      ]
    }
  },
  computed: {
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