<template>
  <!-- Only show content when not loading -->
  <div v-if="!isLoading">
    <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
      <template #role-content>
        <div class="space-y-6">
          <!-- Stats Overview -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-blue-50 rounded-lg">
                  <span class="material-icons text-blue-600">school</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.enrolledCourses }}</div>
                  <div class="text-sm text-gray-600">Enrolled Courses</div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-green-50 rounded-lg">
                  <span class="material-icons text-green-600">assignment_turned_in</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.completedAssignments }}</div>
                  <div class="text-sm text-gray-600">Completed Assignments</div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-purple-50 rounded-lg">
                  <span class="material-icons text-purple-600">stars</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.averageGrade }}%</div>
                  <div class="text-sm text-gray-600">Average Grade</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Current Courses -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-gray-800">Enrolled Courses</h3>
              <router-link to="/student/courses" class="text-maroon-600 hover:text-maroon-700 text-sm font-medium">
                View All Courses
              </router-link>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div v-for="course in enrolledCourses" :key="course.id" 
                   class="flex flex-col md:flex-row items-start space-y-4 md:space-y-0 md:space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div class="w-full md:w-24 h-24 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                  <img :src="course.imageUrl" class="w-full h-full object-cover" :alt="course.title">
                </div>
                <div class="flex-grow">
                  <h4 class="font-semibold text-lg text-gray-900">{{ course.title }}</h4>
                  <div class="text-sm text-gray-600 mb-2">{{ course.instructor }}</div>
                  <div class="flex items-center space-x-4">
                    <div class="flex items-center">
                      <span class="material-icons text-yellow-500 text-sm mr-1">schedule</span>
                      <span class="text-xs text-gray-600">{{ course.duration }}</span>
                    </div>
                    <div class="flex items-center">
                      <span class="material-icons text-maroon-500 text-sm mr-1">assignment</span>
                      <span class="text-xs text-gray-600">{{ course.assignments }} assignments</span>
                    </div>
                  </div>
                  <div class="mt-2">
                    <div class="w-full bg-gray-200 rounded-full h-1.5">
                      <div class="bg-maroon-600 h-1.5 rounded-full" :style="{ width: course.progress + '%' }"></div>
                    </div>
                    <div class="text-xs text-gray-600 mt-1">{{ course.progress }}% completed</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Upcoming Assignments -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-gray-800">Upcoming Assignments</h3>
              <router-link to="/student/assignments" class="text-maroon-600 hover:text-maroon-700 text-sm font-medium">
                View All Assignments
              </router-link>
            </div>
            <div class="space-y-4">
              <div v-for="assignment in upcomingAssignments" :key="assignment.id" 
                  class="flex flex-col md:flex-row items-start md:items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div class="flex items-start space-x-4 mb-4 md:mb-0">
                  <div :class="['p-2 rounded-lg', assignment.iconBg]">
                    <span class="material-icons" :class="assignment.iconColor">{{ assignment.icon }}</span>
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-900">{{ assignment.title }}</h4>
                    <div class="text-sm text-gray-600">{{ assignment.course }}</div>
                    <div class="text-xs text-gray-500 mt-1">Due: {{ assignment.dueDate }}</div>
                  </div>
                </div>
                <div class="flex items-center space-x-2 w-full md:w-auto">
                  <button :class="['px-3 py-1.5 text-sm font-medium rounded-lg', 
                    assignment.status === 'Not Started' ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' : 
                    assignment.status === 'In Progress' ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' :
                    'bg-green-100 text-green-800 hover:bg-green-200']">
                    {{ assignment.status }}
                  </button>
                  <router-link :to="`/student/assignments/${assignment.id}`"
                  class="px-3 py-1.5 bg-maroon-600 text-white text-sm font-medium rounded-lg hover:bg-maroon-700 transition-colors">
                    View
                  </router-link>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div class="flex items-center justify-between mb-6">
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
  name: 'StudentProfilePage',
  components: {
    BaseProfilePage
  },
  data() {
    return {
      userType: 'student',
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
      activityFilters: [
        { label: 'All', value: 'all' },
        { label: 'Courses', value: 'courses' },
        { label: 'Assignments', value: 'assignments' }
      ],
      recentActivities: [
        {
          id: 1,
          icon: 'book',
          title: 'Enrolled in New Course',
          description: 'You enrolled in "Advanced Web Development"',
          timestamp: '2 hours ago',
          type: 'courses'
        },
        {
          id: 2,
          icon: 'assignment_turned_in',
          title: 'Assignment Submitted',
          description: 'Submitted "Data Structures Lab 3" for CS101',
          timestamp: '5 hours ago',
          type: 'assignments'
        },
        {
          id: 3,
          icon: 'grade',
          title: 'Grade Received',
          description: 'You got 95% on "JavaScript Fundamentals Quiz"',
          timestamp: '1 day ago',
          type: 'assignments'
        }
      ],
      stats: {
        enrolledCourses: 4,
        completedAssignments: 18,
        averageGrade: 92
      },
      enrolledCourses: [
        {
          id: 1,
          title: 'Introduction to Computer Science',
          instructor: 'Dr. Jane Smith',
          imageUrl: 'https://picsum.photos/id/0/200',
          duration: '12 weeks',
          assignments: 10,
          progress: 75
        },
        {
          id: 2,
          title: 'Web Development Fundamentals',
          instructor: 'Prof. Michael Johnson',
          imageUrl: 'https://picsum.photos/id/9/200',
          duration: '8 weeks',
          assignments: 6,
          progress: 50
        },
        {
          id: 3,
          title: 'Database Design & SQL',
          instructor: 'Dr. Sarah Williams',
          imageUrl: 'https://picsum.photos/id/2/200',
          duration: '10 weeks',
          assignments: 8,
          progress: 30
        },
        {
          id: 4,
          title: 'Machine Learning Basics',
          instructor: 'Prof. Robert Chen',
          imageUrl: 'https://picsum.photos/id/3/200',
          duration: '14 weeks',
          assignments: 12,
          progress: 10
        }
      ],
      upcomingAssignments: [
        {
          id: 1,
          title: 'Final Project Proposal',
          course: 'Web Development Fundamentals',
          dueDate: 'Tomorrow, 11:59 PM',
          status: 'Not Started',
          icon: 'assignment',
          iconBg: 'bg-red-100',
          iconColor: 'text-red-600'
        },
        {
          id: 2,
          title: 'Data Structures Lab 4',
          course: 'Introduction to Computer Science',
          dueDate: 'Friday, 5:00 PM',
          status: 'In Progress',
          icon: 'code',
          iconBg: 'bg-yellow-100',
          iconColor: 'text-yellow-600'
        },
        {
          id: 3,
          title: 'Database Normalization Quiz',
          course: 'Database Design & SQL',
          dueDate: 'Next Monday, 3:00 PM',
          status: 'Not Started',
          icon: 'quiz',
          iconBg: 'bg-blue-100',
          iconColor: 'text-blue-600'
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