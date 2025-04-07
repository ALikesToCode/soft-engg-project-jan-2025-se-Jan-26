<template>
  <div class="error-container">
    <div class="error-icon">
      <span class="material-symbols-outlined text-red-500 text-3xl">error_outline</span>
    </div>
    <h3 class="error-title">{{ title }}</h3>
    <p class="error-message">{{ message }}</p>
    <button 
      v-if="retryAction" 
      @click="retryAction" 
      class="retry-button"
    >
      <span class="material-symbols-outlined mr-1">refresh</span>
      Retry
    </button>
  </div>
</template>

<script>
export default {
  name: 'ErrorState',
  props: {
    title: {
      type: String,
      default: 'Something went wrong'
    },
    message: {
      type: String,
      default: 'We encountered an error while loading the content. Please try again.'
    },
    retryAction: {
      type: Function,
      default: null
    }
  }
}
</script>

<style scoped>
.error-container {
  @apply flex flex-col items-center justify-center p-8 text-center;
}

.error-icon {
  @apply mb-4;
}

.error-title {
  @apply text-lg font-medium text-slate-800 mb-2;
}

.error-message {
  @apply text-slate-600 mb-6;
}

.retry-button {
  @apply flex items-center justify-center px-4 py-2 bg-maroon-600 text-white rounded-lg 
         hover:bg-maroon-700 transition-colors focus:outline-none focus:ring-2 
         focus:ring-maroon-500 focus:ring-offset-2;
}
</style> 