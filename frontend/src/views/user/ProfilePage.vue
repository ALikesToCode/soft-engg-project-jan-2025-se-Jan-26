<template>
  <!-- Only show content when not loading -->
  <div v-if="!isLoading">
    <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
      <template #role-content>
        <div>
          <h2 class="text-2xl font-bold text-gray-800 mb-4">My Enrolled Courses</h2>
          <StudentCourseList :courses="courses" @continue-course="continueCourseToDashboard" />
        </div>
      </template>
    </BaseProfilePage>
  </div>
  
  <!-- Loading Overlay - Always visible when loading -->
  <div v-if="isLoading" class="loading-overlay">
    <div class="loading-container">
      <LoadingSpinner size="large" />
      <p class="loading-text">Loading your profile...</p>
    </div>
  </div>
</template>

<script>
import BaseProfilePage from '../base/BaseProfilePage.vue'
import StudentCourseList from './components/StudentCourseList.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { Course } from '@/models/Course'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
const dummyAvatar =
  'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iMzYiIHI9IjIwIiBmaWxsPSIjOTA5MDkwIi8+PHBhdGggZD0iTTIwLDg1IEMzMCw2NSA3MCw2NSA4MCw4NSIgZmlsbD0iIzkwOTA5MCIvPjwvc3ZnPg=='

export default {
  name: 'StudentProfilePage',
  components: {
    BaseProfilePage,
    StudentCourseList,
    LoadingSpinner,
  },
  props: {
    // userInfo: {
    //   type: Object,
    //   required: true,
    // },
    initialCourses: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      userType: 'student',
      courses: [],
      userInfo: {
        id: null,
        name: null,
        email: null,
        profilePictureUrl: dummyAvatar,
        coursesCount: 5,
        studentsCount: 0,
        rating: 4.5,
      },
      isProfileDataLoading: false,
      isCourseEnrolledDataLoading: false,
    }
  },
  computed: {
    isLoading() {
      return this.isProfileDataLoading || this.isCourseEnrolledDataLoading;
    }
  },
  methods: {
    showSuccessToast(msg) {
      const toast = useToast() // Call inside the method
      toast.success(msg, { timeout: 3000 })
    },
    showErrorToast(error, defaultMessage) {
      const toast = useToast()
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    },
    continueCourseToDashboard() {
      this.$router.push({ path: '/user/courses' })
    },

    // Combined data loading method
    async loadData() {
      this.isProfileDataLoading = true
      this.isCourseEnrolledDataLoading = true
      
      try {
        // Get token once
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')
        
        const headers = {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
        
        // Load profile data first
        await this.getUserProfile(headers)
        
        // Then load courses
        await this.getUserEnrolledCourses(headers)
        
      } catch (error) {
        console.error('Error loading data:', error)
        this.showErrorToast(error, 'Failed to load user data')
      } finally {
        // Ensure loading states are cleared even if errors occur
        this.isProfileDataLoading = false
        this.isCourseEnrolledDataLoading = false
      }
    },

    //APIs
    async getUserProfile(headers) {
      try {
        const response = await api.get('/user/profile', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user profile data')

        console.log('Profile data received:', response.data)
        console.log('Profile picture URL:', response.data.profile_pic_url)

        this.userInfo.id = response.data.id
        this.userInfo.name = response.data.name
        this.userInfo.email = response.data.email
        this.userInfo.profilePictureUrl = response.data.profile_pic_url || this.userInfo.profilePictureUrl
        
        this.showSuccessToast('Profile loaded successfully')
        return true
      } catch (error) {
        console.error('Error fetching user profile:', error)
        throw error
      }
    },
    
    async getUserEnrolledCourses(headers) {
      try {
        const response = await api.get('/user/courses', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user course data')

        // Clear existing courses
        this.courses = []
        
        response.data.forEach((c) => {
          const course = new Course({
            id: c.id,
            title: c.title,
            description: c.description,
            status: c.status,
            progress: 50,
            duration: c.duration + ' Weeks',
            studentsCount: 100,
            instructor: { name: c.created_by, avatar: dummyAvatar },
          })
          this.courses.push(course)
        })
        
        console.log('Courses loaded:', this.courses.length)
        return true
      } catch (error) {
        console.error('Error fetching user courses:', error)
        throw error
      }
    },
  },
  mounted() {
    this.loadData()
  },
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}
.aspect-w-16 {
  position: relative;
  padding-bottom: 56.25%;
}

.aspect-w-16 iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50;
}

.loading-container {
  @apply bg-white rounded-lg p-8 flex flex-col items-center justify-center;
  min-width: 250px;
}

.loading-text {
  @apply mt-4 text-lg font-medium text-gray-700;
}
</style>
