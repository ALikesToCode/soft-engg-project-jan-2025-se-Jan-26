<template>
  <div class="loading-container">
    <div class="spinner"></div>
    <p v-if="message" class="loading-message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingState',
  props: {
    message: {
      type: String,
      default: 'Loading content...'
    }
  }
}
</script>

<style scoped>
.loading-container {
  @apply flex flex-col items-center justify-center p-8;
}

.spinner {
  @apply w-12 h-12 border-4 border-maroon-500 border-t-transparent rounded-full animate-spin;
}

.loading-message {
  @apply mt-4 text-slate-600 text-center;
}
</style> 