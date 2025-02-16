<template>
  <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
    <template #role-content>
      <div>
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
    </template>
  </BaseProfilePage>
</template>

<script>
import BaseProfilePage from '../base/BaseProfilePage.vue'
import FacultyCourseList from '../user/components/FacultyCourseList.vue'
import ContentOrderingPreview from '../user/components/ContentOrderingPreview.vue'

export default {
  name: 'FacultyProfilePage',
  components: {
    BaseProfilePage,
    FacultyCourseList,
    ContentOrderingPreview
  },
  props: {
    userInfo: {
      type: Object,
      required: true
    },
    initialCourses: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      userType: 'faculty',
      courses: [...this.initialCourses],
      isDirty: false
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
    }
  },
  beforeUnload(e) {
    if (this.isDirty) {
      e.preventDefault()
      e.returnValue = ''
    }
  }
}
</script> 