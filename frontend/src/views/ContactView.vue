<template>
  <div class="min-h-screen bg-gray-50 pt-16 sm:pt-20">
    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-maroon-600 via-maroon-700 to-maroon-800 text-white py-12">
      <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Contact Us
          </h1>
          <p class="text-xl text-gray-200">
            Get in touch with Team 26
          </p>
        </div>
      </div>
    </div>

    <!-- Contact Section -->
    <div class="py-12 bg-white">
      <div class="container mx-auto px-4">
        <div class="max-w-2xl mx-auto">
          <div class="bg-gray-50 rounded-xl p-8 shadow-lg text-center">
            <div class="flex items-center justify-center mb-6">
              <span class="material-icons text-4xl text-maroon-600">email</span>
            </div>
            <h2 class="text-2xl font-bold text-gray-800 mb-4">Email Us</h2>
            <p class="text-gray-600 mb-6">Feel free to reach out to us at:</p>
            <a href="mailto:abhyudaya@aloves.codes" class="text-xl text-maroon-600 hover:text-maroon-700 font-medium flex items-center justify-center">
              <span class="material-icons mr-2">mail</span>
              abhyudaya@aloves.codes
            </a>
            <p class="text-gray-500 mt-6 text-sm">We'll get back to you as soon as possible.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactView'
}
</script>

<style scoped>
.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style> 