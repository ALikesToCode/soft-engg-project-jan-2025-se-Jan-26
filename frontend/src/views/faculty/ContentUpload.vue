<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="w-1/2 max-w-lg bg-white p-6 rounded shadow space-y-4">
      <!-- Top Section with 3 Select Boxes -->
      <div class="flex justify-start gap-6 gap-y-6">
        <select v-model="selectedCourse" class="basis-2/3 px-4 py-2 bg-red-700 text-white rounded">
          <option disabled value="">Course</option>
          <option v-for="course in courses" :key="course">{{ course }}</option>
        </select>
        <select v-model="selectedWeek" class="px-4 py-2 bg-red-700 text-white rounded">
          <option disabled value="">Week</option>
          <option v-for="week in weeks" :key="week">{{ week }}</option>
        </select>
        <select v-model="selectedLecture" class="px-4 py-2 bg-red-700 text-white rounded">
          <option disabled value="">Lecture</option>
          <option v-for="num in 12" :key="num">{{ num }}</option>
        </select>
      </div>
      <br>
      <div>
        <input type="text" v-model="title" placeholder="Title" class="w-full p-3 my-4 border border-red-700 rounded focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700">
      </div>
      <br>
      <div>
        <textarea v-model="description" placeholder="Description" class="w-full p-3 border border-red-700 rounded focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700"></textarea>
      </div>
      <br>
      <div>
        <input type="text" v-model="videoUrl" placeholder="YouTube Video URL" class="w-full p-3 border border-red-700 rounded focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700">
      </div>
      <br>
      <div class="border-2 border-dashed border-red-700 p-6 text-center rounded-lg cursor-pointer hover:bg-red-100" @click="uploadFile">
        <span class="text-2xl font-bold">+</span><br>
        <span class="text-gray-600">Upload Transcript</span>
      </div>
      <br>
      <div class="flex justify-center items-center">
            <button class="bg-red-700 w-1/2 text-white px-6 py-2 rounded hover:bg-red-800 transition" @click="saveForm">
                Save
            </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      courses: ['Math', 'CT', 'Stats', 'Python'],
      weeks: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      selectedCourse: '',
      selectedWeek: '',
      selectedLecture: '',
      title: '',
      description: '',
      videoUrl: ''
    };
  },
  methods: {
    uploadFile() {
      alert("Upload file clicked!");
    },
    saveForm() {
      alert("Form saved!");
    }
  }
};
</script>

<style scoped>
/* No extra styles needed since we're using Tailwind */
</style>
