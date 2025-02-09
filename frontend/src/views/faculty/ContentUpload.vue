<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50">
    <div class="w-full max-w-2xl bg-white p-8 rounded-xl shadow-lg space-y-6 transition-all duration-300">
      <!-- Form Header -->
      <div class="space-y-2 border-b border-gray-200 pb-6">
        <h1 class="text-2xl font-bold text-maroon-800">Course Content Upload</h1>
        <p class="text-gray-600">Upload lecture materials and manage course content</p>
      </div>

      <!-- Selection Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700">Course</label>
          <select v-model="selectedCourse" class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 transition">
            <option disabled value="">Select course</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.name }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700">Week</label>
          <select v-model="selectedWeek" class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 transition">
            <option disabled value="">Select week</option>
            <option v-for="week in 12" :key="week" :value="week">Week {{ week }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700">Lecture</label>
          <select v-model="selectedLecture" class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 transition">
            <option disabled value="">Select lecture</option>
            <option v-for="num in 12" :key="num" :value="num">Lecture {{ num }}</option>
          </select>
        </div>
      </div>

      <!-- Form Fields -->
      <div class="space-y-4">
        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700">Lecture Title</label>
          <input type="text" v-model="title" placeholder="Enter lecture title" class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 placeholder-gray-400 transition">
        </div>

        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700">Description</label>
          <textarea v-model="description" placeholder="Add lecture description" rows="3" class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 placeholder-gray-400 transition"></textarea>
        </div>

        <div class="space-y-1">
          <label class="block text-sm font-medium text-gray-700">YouTube URL</label>
          <div class="relative">
            <input type="url" v-model="videoUrl" placeholder="https://youtube.com/..." class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 placeholder-gray-400 transition pr-12">
            <span class="absolute right-3 top-3 text-gray-400">
              <i class="fab fa-youtube text-xl"></i>
            </span>
          </div>
        </div>

        <!-- File Upload -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700">Course Materials</label>
          <div @click="uploadFile" class="border-2 border-dashed border-gray-300 p-6 text-center rounded-xl cursor-pointer hover:border-maroon-500 hover:bg-maroon-50 transition-colors group">
            <div class="flex flex-col items-center space-y-2">
              <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 group-hover:text-maroon-600 transition"></i>
              <p class="text-sm text-gray-600 group-hover:text-maroon-800 transition">
                <span class="font-medium">Click to upload</span> or drag and drop
              </p>
              <p class="text-xs text-gray-500">PDF, DOCX, PPTX (max 50MB)</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <button @click="saveForm" :disabled="isSaving" class="w-full py-3 px-6 bg-maroon-600 hover:bg-maroon-700 text-white font-medium rounded-lg transition-all duration-300 flex items-center justify-center">
        <i v-if="isSaving" class="fas fa-spinner fa-spin mr-2"></i>
        {{ isSaving ? 'Saving...' : 'Publish Content' }}
      </button>

      <!-- Success/Error Messages -->
      <div v-if="successMessage" class="p-4 bg-green-50 text-green-700 rounded-lg">
        <i class="fas fa-check-circle mr-2"></i>{{ successMessage }}
      </div>
      <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-lg">
        <i class="fas fa-exclamation-circle mr-2"></i>{{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      courses: [
        { id: 'math101', name: 'Mathematics Fundamentals' },
        { id: 'ct201', name: 'Computational Thinking' },
        { id: 'stats301', name: 'Applied Statistics' },
        { id: 'python401', name: 'Python Programming' }
      ],
      selectedCourse: '',
      selectedWeek: '',
      selectedLecture: '',
      title: '',
      description: '',
      videoUrl: '',
      isSaving: false,
      successMessage: '',
      errorMessage: ''
    };
  },
  methods: {
    async uploadFile() {
      try {
        // Implement actual file upload logic
        const file = await this.$refs.fileInput.files[0];
        if (file) {
          // Handle file upload
        }
      } catch (error) {
        this.errorMessage = 'Error uploading file: ' + error.message;
      }
    },
    async saveForm() {
      try {
        this.isSaving = true;
        // Implement form validation and submission
        if (!this.validateForm()) return;

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        this.successMessage = 'Content published successfully!';
        this.resetForm();
      } catch (error) {
        this.errorMessage = 'Error saving content: ' + error.message;
      } finally {
        this.isSaving = false;
      }
    },
    validateForm() {
      if (!this.selectedCourse || !this.selectedWeek || !this.selectedLecture) {
        this.errorMessage = 'Please select course, week, and lecture';
        return false;
      }
      if (!this.title.trim()) {
        this.errorMessage = 'Lecture title is required';
        return false;
      }
      return true;
    },
    resetForm() {
      this.selectedCourse = '';
      this.selectedWeek = '';
      this.selectedLecture = '';
      this.title = '';
      this.description = '';
      this.videoUrl = '';
    }
  }
};
</script>
