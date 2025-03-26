<template>
  <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
    <template #role-content>
      <div>
        <h2 class="text-2xl font-bold text-gray-800 mb-4">My Enrolled Courses</h2>
        <StudentCourseList :courses="courses" @continue-course="continueCourseToDashboard" />
      </div>
    </template>
  </BaseProfilePage>
  <!-- Loading Overlay -->
  <div v-if="isProfileDataLoading || isCourseEnrolledDataLoading" class="loading-overlay">
    <LoadingSpinner />
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

    //APIs
    async getUserProfile() {
      try {
        this.isProfileDataLoading = true
        const token = localStorage.getItem('token') // Retrieve token from localStorage
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.get('/user/profile', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user profile data')

        this.userInfo.id = response.data.id
        this.userInfo.name = response.data.name
        this.userInfo.email = response.data.email
        this.userInfo.profilePictureUrl = response.data.profile_pic_url
        this.isProfileDataLoading = false
        this.showSuccessToast('Successfully fetched user profile data')
        console.log(response.data)
      } catch (error) {
        this.isProfileDataLoading = false
        this.showErrorToast(error, 'Failed to fetch user profile data')
        console.error('Error fetching user profile:', error)
      }
    },
    async getUserEnrolledCourses() {
      try {
        this.isCourseEnrolledDataLoading = true
        const token = localStorage.getItem('token') // Retrieve token from localStorage
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        const response = await api.get('/user/courses', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user course data')

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
        this.isCourseEnrolledDataLoading = false
        console.log('c = ' + this.courses)
        this.showSuccessToast('User course data fetched successfully')
      } catch (error) {
        this.isCourseEnrolledDataLoading = false
        this.showErrorToast(error, 'Failed to fetch user course data')
        console.error('Error fetching user courses:', error)
      }
    },
  },
  mounted() {
    this.getUserProfile(), this.getUserEnrolledCourses()
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
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
