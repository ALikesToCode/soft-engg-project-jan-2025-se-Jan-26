<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Profile Header -->
      <ProfileHeader :user="userInfo" :userType="userType" />

      <!-- Role-specific content -->
      <div v-if="userType === 'faculty'" class="mt-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-gray-800">My Courses</h2>
          <div class="flex space-x-4">
            <button
              @click="saveCourseOrder"
              class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
            >
              Save Order
            </button>
          </div>
        </div>

        <!-- Faculty course list with ordering -->
        <FacultyCourseList v-model="courses" @order-updated="handleOrderUpdate" />

        <!-- Preview of the ordering -->
        <ContentOrderingPreview :courses="courses" class="mt-6" />
      </div>

      <div v-else-if="userType === 'student'" class="mt-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">My Enrolled Courses</h2>
        <StudentCourseList :courses="courses" />
      </div>

      <div v-if="userType === 'support'">
        <div>Support</div>
      </div>

      <div v-else class="mt-6">
        <p class="text-gray-600">No courses to display.</p>
      </div>
    </div>
  </div>
</template>

<script>
import ProfileHeader from './components/ProfileHeader.vue'
import FacultyCourseList from './components/FacultyCourseList.vue'
import StudentCourseList from './components/StudentCourseList.vue'
import ContentOrderingPreview from './components/ContentOrderingPreview.vue'

export default {
  name: 'ProfilePage',
  components: {
    ProfileHeader,
    FacultyCourseList,
    StudentCourseList,
    ContentOrderingPreview,
  },
  props: {
    userType: {
      type: String,
      required: true,
      validator: (value) => ['faculty', 'student'].includes(value),
    },
    userInfo: {
      type: Object,
      required: true,
    },
    initialCourses: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      courses: [...this.initialCourses],
      isDirty: false,
    }
  },
  methods: {
    handleOrderUpdate() {
      this.isDirty = true
    },
    async saveCourseOrder() {
      try {
        // TODO: Implement API call to save course order
        this.isDirty = false
        this.$toast.success('Course order saved successfully')
      } catch (error) {
        this.$toast.error('Failed to save course order')
      }
    },
  },
  beforeUnload(e) {
    if (this.isDirty) {
      e.preventDefault()
      e.returnValue = ''
    }
  },
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}
</style>
