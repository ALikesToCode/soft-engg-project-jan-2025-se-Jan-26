<template>
  <div class="p-4 bg-white rounded-lg shadow-sm border border-slate-200">
    <div class="text-center">
      <h3 class="text-lg font-medium text-slate-900 mb-2">Discussion Forum</h3>
      <p class="text-sm text-slate-500 mb-4">
        Discussion functionality will be implemented soon.
      </p>
      <div class="inline-block p-4 bg-slate-100 rounded-full">
        <span class="material-symbols-outlined text-slate-400 text-3xl">forum</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommunityDialogue',
  props: {
    lectureId: {
      type: [String, Number],
      required: true
    },
    courseId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      discussions: [],
      loading: false,
      error: null,
      newComment: ''
    }
  },
  methods: {
    // These methods will be implemented when the backend API is ready
    async loadDiscussions() {
      this.loading = true;
      try {
        // Mock API call
        console.log(`Loading discussions for lecture ${this.lectureId} in course ${this.courseId}`);
        setTimeout(() => {
          this.discussions = [];
          this.loading = false;
        }, 500);
      } catch (error) {
        this.error = "Failed to load discussions";
        this.loading = false;
      }
    }
  },
  mounted() {
    // Will call loadDiscussions when the component is ready
    console.log('CommunityDialogue component mounted');
  }
}
</script>

<style scoped>
.discussion-container {
  max-height: 400px;
  overflow-y: auto;
}
</style> 