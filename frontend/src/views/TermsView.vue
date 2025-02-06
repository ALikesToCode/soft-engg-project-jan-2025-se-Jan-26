<template>
  <div class="min-h-screen bg-gray-50 pt-16 sm:pt-20">
    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-maroon-600 via-maroon-700 to-maroon-800 text-white py-12">
      <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Terms of Service
          </h1>
          <p class="text-xl text-gray-200">
            Guidelines for using AI Academic Guide
          </p>
        </div>
      </div>
    </div>

    <!-- Content Section -->
    <div class="py-12 bg-white">
      <div class="container mx-auto px-4">
        <div class="max-w-3xl mx-auto prose prose-maroon">
          <div class="space-y-8">
            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">gavel</span>
                Acceptance of Terms
              </h2>
              <p class="text-gray-600">
                By accessing and using AI Academic Guide, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using this service.
              </p>
            </section>

            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">school</span>
                Academic Integrity
              </h2>
              <p class="text-gray-600">
                Users must maintain academic integrity while using our services. Any form of cheating, plagiarism, or misuse of the platform will result in immediate account suspension.
              </p>
            </section>

            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">account_circle</span>
                User Responsibilities
              </h2>
              <p class="text-gray-600">
                You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. Any unauthorized use must be reported immediately.
              </p>
            </section>

            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">policy</span>
                Service Modifications
              </h2>
              <p class="text-gray-600">
                We reserve the right to modify or discontinue the service at any time, with or without notice. We shall not be liable to you or any third party for any modification, suspension, or discontinuance of the service.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TermsView'
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