<template>
  <div class="relative bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
    <div class="aspect-w-16 aspect-h-9">
      <iframe
        :src="videoUrl"
        class="w-full h-full"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>
    <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-gray-900/80 to-transparent p-4">
      <div class="flex items-center justify-between text-white/90">
        <div class="flex items-center space-x-4">
          <button class="p-2 hover:text-white transition-colors">
            <i class="fas fa-step-backward text-xl"></i>
          </button>
          <button class="w-12 h-12 rounded-full bg-primary-500/90 hover:bg-primary-500 text-white 
                      flex items-center justify-center transition-all duration-300 hover:scale-105">
            <i class="fas fa-play text-lg"></i>
          </button>
          <button class="p-2 hover:text-white transition-colors">
            <i class="fas fa-step-forward text-xl"></i>
          </button>
        </div>
        <div class="flex items-center space-x-4">
          <button class="p-2 hover:text-white transition-colors">
            <i class="fas fa-closed-captioning text-xl"></i>
          </button>
          <button class="p-2 hover:text-white transition-colors">
            <i class="fas fa-cog text-xl"></i>
          </button>
          <button class="p-2 hover:text-white transition-colors">
            <i class="fas fa-expand text-xl"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseVideoPlayer',
  props: {
    videoUrl: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.aspect-w-16 {
  @apply relative overflow-hidden rounded-xl;
  padding-bottom: 56.25%;
}

.aspect-w-16 > * {
  @apply absolute inset-0 w-full h-full object-cover;
}
</style> 