<template>
  <BaseProfilePage :user-type="userType" :user-info="userInfo" :is-editable="true">
    <template #role-content>
      <div>
        <h2 class="text-2xl font-bold text-gray-800 mb-4">My Enrolled Courses</h2>
        <StudentCourseList :courses="courses" />
      </div>
    </template>
  </BaseProfilePage>
</template>

<script>
import BaseProfilePage from '../base/BaseProfilePage.vue'
import StudentCourseList from './components/StudentCourseList.vue'

export default {
  name: 'StudentProfilePage',
  components: {
    BaseProfilePage,
    StudentCourseList
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
      userType: 'student',
      courses: [...this.initialCourses]
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}
</style>
