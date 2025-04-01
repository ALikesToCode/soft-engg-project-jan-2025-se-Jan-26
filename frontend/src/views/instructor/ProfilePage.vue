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
                  <span class="material-icons text-blue-600">school</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.totalCourses }}</div>
                  <div class="text-sm text-gray-600">Total Courses</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">trending_up</span>
                  +2 this month
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-green-50 rounded-lg">
                  <span class="material-icons text-green-600">people</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.totalStudents }}</div>
                  <div class="text-sm text-gray-600">Total Students</div>
                </div>
              </div>
              <div class="mt-2 text-sm">
                <span class="text-green-600 flex items-center">
                  <span class="material-icons text-sm mr-1">trending_up</span>
                  +45 this month
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-purple-50 rounded-lg">
                  <span class="material-icons text-purple-600">assignment</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.assignmentsPending }}</div>
                  <div class="text-sm text-gray-600">Pending Reviews</div>
                </div>
              </div>
              <div class="mt-2">
                <div class="w-full bg-gray-100 rounded-full h-1.5">
                  <div class="bg-purple-500 h-1.5 rounded-full" :style="{ width: pendingAssignmentsPercentage + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center space-x-4">
                <div class="p-3 bg-yellow-50 rounded-lg">
                  <span class="material-icons text-yellow-600">star</span>
                </div>
                <div>
                  <div class="text-2xl font-bold text-gray-900">{{ stats.averageRating }}</div>
                  <div class="text-sm text-gray-600">Average Rating</div>
                </div>
              </div>
              <div class="mt-2 flex">
                <div class="flex">
                  <span v-for="i in 5" :key="i" class="material-icons text-yellow-400 text-sm">
                    {{ i <= Math.floor(stats.averageRating) ? 'star' : (i - stats.averageRating < 1 ? 'star_half' : 'star_border') }}
                  </span>
                </div>
                <span class="text-gray-500 text-xs ml-2">({{ stats.totalRatings }} reviews)</span>
              </div>
            </div>
          </div>

          <!-- Courses & Students -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Active Courses -->
            <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">Active Courses</h3>
                <router-link to="/instructor/courses" class="text-maroon-600 hover:text-maroon-700 text-sm font-medium">
                  View All Courses
                </router-link>
              </div>
              <div class="space-y-6">
                <div v-for="course in activeCourses" :key="course.id" 
                    class="flex flex-col md:flex-row items-start space-y-4 md:space-y-0 md:space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div class="w-full md:w-24 h-24 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                    <img :src="course.imageUrl" class="w-full h-full object-cover" :alt="course.title">
                  </div>
                  <div class="flex-grow">
                    <div class="flex items-start justify-between">
                      <div>
                        <h4 class="font-semibold text-lg text-gray-900">{{ course.title }}</h4>
                        <div class="text-sm text-gray-600 mb-2">{{ course.students }} students enrolled</div>
                      </div>
                      <div class="flex items-center space-x-1">
                        <span class="material-icons text-yellow-400 text-sm">star</span>
                        <span class="text-sm font-medium">{{ course.rating }}</span>
                      </div>
                    </div>
                    <div class="flex flex-wrap items-center gap-2 mt-2">
                      <span v-for="tag in course.tags" :key="tag" 
                            class="px-2 py-1 bg-gray-200 text-gray-700 text-xs font-medium rounded-full">
                        {{ tag }}
                      </span>
                    </div>
                    <div class="flex items-center justify-between mt-3">
                      <div class="text-sm text-gray-600">Last updated: {{ course.lastUpdated }}</div>
                      <div class="flex space-x-2">
                        <router-link :to="`/instructor/courses/${course.id}`"
                           class="px-3 py-1 bg-maroon-600 text-white text-sm font-medium rounded-lg hover:bg-maroon-700 transition-colors">
                          Manage
                        </router-link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Students -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">Recent Students</h3>
                <router-link to="/instructor/students" class="text-maroon-600 hover:text-maroon-700 text-sm font-medium">
                  View All
                </router-link>
              </div>
              <div class="space-y-4">
                <div v-for="student in recentStudents" :key="student.id" 
                     class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full overflow-hidden">
                      <img :src="student.avatar" class="w-full h-full object-cover" alt="">
                    </div>
                    <div>
                      <div class="font-medium text-gray-900">{{ student.name }}</div>
                      <div class="text-xs text-gray-600">{{ student.course }}</div>
                    </div>
                  </div>
                  <div class="text-xs text-gray-500">{{ student.enrolledDate }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Assignments & Schedule -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Pending Assignments -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">Pending Assignments</h3>
                <router-link to="/instructor/assignments" class="text-maroon-600 hover:text-maroon-700 text-sm font-medium">
                  View All
                </router-link>
              </div>
              <div class="space-y-4">
                <div v-for="assignment in pendingAssignments" :key="assignment.id" 
                     class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div class="flex items-start space-x-3">
                    <span class="material-icons text-maroon-600">assignment</span>
                    <div>
                      <div class="font-medium text-gray-900">{{ assignment.title }}</div>
                      <div class="text-xs text-gray-600">{{ assignment.course }} • {{ assignment.submissions }} submissions</div>
                      <div class="text-xs text-gray-500 mt-1">Due: {{ assignment.dueDate }}</div>
                    </div>
                  </div>
                  <router-link :to="`/instructor/assignments/${assignment.id}`"
                     class="px-3 py-1 bg-maroon-600 text-white text-xs font-medium rounded-lg hover:bg-maroon-700 transition-colors">
                    Review
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Teaching Schedule -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-gray-800">Teaching Schedule</h3>
                <div class="text-xs text-gray-600">{{ currentDate }}</div>
              </div>
              <div class="space-y-4">
                <div v-for="session in upcomingSessions" :key="session.id" 
                     class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div class="p-2 rounded-lg" :class="session.colorClass">
                    <span class="material-icons text-white">{{ session.icon }}</span>
                  </div>
                  <div class="flex-grow">
                    <div class="flex items-start justify-between">
                      <div>
                        <div class="font-medium text-gray-900">{{ session.title }}</div>
                        <div class="text-xs text-gray-600">{{ session.course }}</div>
                      </div>
                      <div class="text-xs font-medium" :class="session.statusClass">
                        {{ session.status }}
                      </div>
                    </div>
                    <div class="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                      <div class="flex items-center">
                        <span class="material-icons text-gray-400 text-sm mr-1">schedule</span>
                        {{ session.time }}
                      </div>
                      <div class="flex items-center">
                        <span class="material-icons text-gray-400 text-sm mr-1">people</span>
                        {{ session.attendees }} attendees
                      </div>
                    </div>
                    <div class="mt-3">
                      <button v-if="session.status === 'Upcoming'" 
                              class="px-3 py-1 bg-maroon-600 text-white text-xs font-medium rounded-lg hover:bg-maroon-700 transition-colors">
                        Start Session
                      </button>
                      <button v-else-if="session.status === 'In Progress'" 
                              class="px-3 py-1 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 transition-colors">
                        Join Now
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Student Feedback -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">Recent Student Feedback</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="feedback in studentFeedback" :key="feedback.id" 
                   class="p-4 bg-gray-50 rounded-lg">
                <div class="flex items-start justify-between">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full overflow-hidden">
                      <img :src="feedback.studentAvatar" class="w-full h-full object-cover" alt="">
                    </div>
                    <div>
                      <div class="font-medium text-gray-900">{{ feedback.studentName }}</div>
                      <div class="text-xs text-gray-600">{{ feedback.course }}</div>
                    </div>
                  </div>
                  <div class="flex">
                    <span v-for="i in 5" :key="i" class="material-icons text-yellow-400 text-sm">
                      {{ i <= feedback.rating ? 'star' : 'star_border' }}
                    </span>
                  </div>
                </div>
                <div class="mt-3 text-sm text-gray-700">
                  "{{ feedback.comment }}"
                </div>
                <div class="mt-2 text-xs text-gray-500">{{ feedback.date }}</div>
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
  name: 'InstructorProfilePage',
  components: {
    BaseProfilePage
  },
  data() {
    return {
      userType: 'instructor',
      isLoading: true,
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
        totalCourses: 5,
        totalStudents: 283,
        assignmentsPending: 18,
        averageRating: 4.8,
        totalRatings: 118
      },
      activeCourses: [
        {
          id: 1,
          title: 'Advanced Web Development',
          students: 68,
          rating: 4.9,
          tags: ['Web', 'JavaScript', 'React'],
          lastUpdated: '3 days ago',
          imageUrl: 'https://picsum.photos/id/1/200'
        },
        {
          id: 2,
          title: 'Introduction to Python Programming',
          students: 104,
          rating: 4.7,
          tags: ['Python', 'Beginner', 'Programming'],
          lastUpdated: '1 week ago',
          imageUrl: 'https://picsum.photos/id/4/200'
        }
      ],
      recentStudents: [
        {
          id: 1,
          name: 'Alex Johnson',
          course: 'Advanced Web Development',
          enrolledDate: '2 days ago',
          avatar: 'https://i.pravatar.cc/150?img=1'
        },
        {
          id: 2,
          name: 'Maya Patel',
          course: 'Introduction to Python Programming',
          enrolledDate: '3 days ago',
          avatar: 'https://i.pravatar.cc/150?img=5'
        },
        {
          id: 3,
          name: 'Thomas Lee',
          course: 'Advanced Web Development',
          enrolledDate: '5 days ago',
          avatar: 'https://i.pravatar.cc/150?img=3'
        },
        {
          id: 4,
          name: 'Emma Wilson',
          course: 'Introduction to Python Programming',
          enrolledDate: '1 week ago',
          avatar: 'https://i.pravatar.cc/150?img=4'
        }
      ],
      pendingAssignments: [
        {
          id: 1,
          title: 'Final Project',
          course: 'Advanced Web Development',
          submissions: 15,
          dueDate: 'Yesterday'
        },
        {
          id: 2,
          title: 'Data Analysis Exercise',
          course: 'Introduction to Python Programming',
          submissions: 22,
          dueDate: '2 days ago'
        },
        {
          id: 3,
          title: 'API Integration Lab',
          course: 'Advanced Web Development',
          submissions: 10,
          dueDate: '3 days ago'
        }
      ],
      currentDate: new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      upcomingSessions: [
        {
          id: 1,
          title: 'Live Coding Session',
          course: 'Advanced Web Development',
          time: 'Today, 2:00 PM - 3:30 PM',
          status: 'Upcoming',
          statusClass: 'text-yellow-600',
          attendees: 42,
          icon: 'code',
          colorClass: 'bg-blue-600'
        },
        {
          id: 2,
          title: 'Office Hours',
          course: 'Introduction to Python Programming',
          time: 'Today, 4:00 PM - 5:00 PM',
          status: 'Upcoming',
          statusClass: 'text-yellow-600',
          attendees: 15,
          icon: 'support_agent',
          colorClass: 'bg-green-600'
        },
        {
          id: 3,
          title: 'Final Project Review',
          course: 'Data Structures & Algorithms',
          time: 'Tomorrow, 10:00 AM - 12:00 PM',
          status: 'Scheduled',
          statusClass: 'text-gray-600',
          attendees: 28,
          icon: 'event',
          colorClass: 'bg-purple-600'
        }
      ],
      studentFeedback: [
        {
          id: 1,
          studentName: 'James Wilson',
          studentAvatar: 'https://i.pravatar.cc/150?img=8',
          course: 'Advanced Web Development',
          rating: 5,
          comment: 'The course material is excellent and the instructor is very knowledgeable. I especially enjoyed the live coding sessions.',
          date: '3 days ago'
        },
        {
          id: 2,
          studentName: 'Sophia Chen',
          studentAvatar: 'https://i.pravatar.cc/150?img=9',
          course: 'Introduction to Python Programming',
          rating: 4,
          comment: 'Great introduction to Python. The assignments were challenging but helped me understand the concepts better.',
          date: '1 week ago'
        },
        {
          id: 3,
          studentName: 'Daniel Martinez',
          studentAvatar: 'https://i.pravatar.cc/150?img=11',
          course: 'Advanced Web Development',
          rating: 5,
          comment: 'One of the best online courses I\'ve taken. The instructor explains complex topics in a simple way.',
          date: '2 weeks ago'
        },
        {
          id: 4,
          studentName: 'Olivia Brown',
          studentAvatar: 'https://i.pravatar.cc/150?img=10',
          course: 'Introduction to Python Programming',
          rating: 5,
          comment: 'I had no programming experience before this course, but now I feel confident in my Python skills. Highly recommend!',
          date: '2 weeks ago'
        }
      ]
    }
  },
  computed: {
    pendingAssignmentsPercentage() {
      // Assuming 30 is the threshold where progress bar would be full
      const maxAssignments = 30
      return (this.stats.assignmentsPending / maxAssignments) * 100
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