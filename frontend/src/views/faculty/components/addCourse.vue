<template>
  <div class="bg-white p-6 rounded-lg max-w-lg w-full mx-auto max-h-[90vh] overflow-y-auto">
    <div class="flex items-center mb-2">
      <div class="flex-1 text-center">
        <miniLoader v-if="course.code === ''"
          >Getting Unique Course Code. Please wait...</miniLoader
        >
        <h2 class="text-xl font-bold text-gray-600">Add A New Course</h2>
      </div>
      <button @click="$emit('close')" class="text-gray-500 hover:text-gray-800 text-2xl">✖</button>
    </div>
    <div class="border-b-[1px] border-maroon-600 mb-4"></div>

    <form @submit.prevent="submitCourse" class="space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Course Name</label>
          <input
            :disabled="course.code === ''"
            v-model="course.name"
            class="input-field"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Course Code</label>
          <input
            :disabled="course.code === ''"
            v-model="course.code"
            class="input-field"
            required
            disabled
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input
            :disabled="course.code === ''"
            v-model="course.title"
            class="input-field"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Credits</label>
          <input
            :disabled="course.code === ''"
            v-model="course.credits"
            type="number"
            class="input-field"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Duration (weeks)</label>
          <input
            :disabled="course.code === ''"
            v-model="course.duration"
            type="number"
            class="input-field"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Semester</label>
          <select
            :disabled="course.code === ''"
            v-model="course.semester"
            class="input-field"
            required
          >
            <option disabled value="">Select Semester</option>
            <option value="Term 1">Term 1</option>
            <option value="Term 2">Term 2</option>
            <option value="Term 3">Term 3</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Year</label>
          <input
            :disabled="course.code === ''"
            v-model="course.year"
            type="number"
            class="input-field"
            required
            size="4"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Level</label>
          <select
            :disabled="course.code === ''"
            v-model="course.level"
            class="input-field"
            required
          >
            <option disabled value="">Select Level</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
          <input
            :disabled="course.code === ''"
            v-model="course.start_date"
            type="date"
            class="input-field"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
          <input disabled v-model="course.end_date" type="date" class="input-field" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Image Url</label>
        <input :disabled="course.code === ''" v-model="course.image" class="input-field" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Syllabus</label>
        <textarea
          :disabled="course.code === ''"
          v-model="course.syllabus"
          class="input-field h-24"
        ></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          :disabled="course.code === ''"
          v-model="course.description"
          class="input-field h-24"
        ></textarea>
      </div>

      <div class="flex justify-end gap-2">
        <button @click="$emit('close')" type="button" class="btn-cancel">Cancel</button>
        <button :disabled="course.code === ''" type="submit" class="btn-submit">Submit</button>
      </div>
    </form>
  </div>
</template>

<script>
import api from '@/utils/api'
import miniLoader from '@/components/common/miniLoader.vue'
export default {
  data() {
    return {
      course: {
        name: '',
        code: '',
        title: '',
        syllabus: '',
        description: '',
        credits: '',
        duration: '',
        semester: '',
        year: '',
        level: '',
        start_date: '',
        end_date: '',
        image: '',
      },
    }
  },
  components: {
    miniLoader,
  },
  methods: {
    submitCourse() {
      // Emit the course data
      this.$emit('course-submitted', this.course)
      // Close modal after submission
      this.$emit('close')
    },

    async getUniqueCourseCode() {
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.get('/course-code', headers)
        this.course.code = response.data.course_code
      } catch (error) {
        this.$emit('course-code-error', 'Failed to get Course Code. Try Again')
        // Delay closing the modal by 2 seconds
        setTimeout(() => {
          this.$emit('close')
        }, 2000)
        console.log('Error=> ' + error)
      }
    },
    updateEndDate() {
      if (this.course.start_date && this.course.duration) {
        const startDate = new Date(this.course.start_date)
        startDate.setDate(startDate.getDate() + this.course.duration * 7) // Convert weeks to days
        this.course.end_date = startDate.toISOString().split('T')[0] // Format as YYYY-MM-DD
      }
    },
  },
  watch: {
    'course.start_date': 'updateEndDate',
    'course.duration': 'updateEndDate',
  },
  mounted() {
    this.getUniqueCourseCode()
  },
}
</script>

<style scoped>
.input-field {
  @apply w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 outline-none;
}
.btn-submit {
  @apply bg-maroon-600 text-white px-5 py-2 rounded-lg hover:bg-maroon-700 transition;
}
.btn-cancel {
  @apply bg-gray-400 text-white px-5 py-2 rounded-lg hover:bg-gray-500 transition;
}
</style>
