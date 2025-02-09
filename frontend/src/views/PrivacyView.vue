<template>
  <div class="min-h-screen bg-gray-50 pt-16 sm:pt-20">
    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-maroon-600 via-maroon-700 to-maroon-800 text-white py-12">
      <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Privacy Policy
          </h1>
          <p class="text-xl text-gray-200">
            How we protect and handle your data
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
                <span class="material-icons text-maroon-600 mr-2">security</span>
                Data Collection and Usage
              </h2>
              <p class="text-gray-600">
                We collect and process only the necessary information required to provide you with our AI Academic Guide services. This includes your basic profile information, academic preferences, and learning patterns to deliver personalized assistance.
              </p>
            </section>

            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">lock</span>
                Data Security
              </h2>
              <p class="text-gray-600">
                Your data is encrypted and stored securely on our servers. We implement industry-standard security measures to protect your information from unauthorized access, disclosure, or misuse.
              </p>
            </section>

            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">share</span>
                Data Sharing
              </h2>
              <p class="text-gray-600">
                We do not share your personal information with third parties without your explicit consent, except as required by law or to provide our core services.
              </p>
            </section>

            <section>
              <h2 class="flex items-center text-2xl font-bold text-gray-900 mb-4">
                <span class="material-icons text-maroon-600 mr-2">update</span>
                Updates to Privacy Policy
              </h2>
              <p class="text-gray-600">
                We may update this privacy policy from time to time. We will notify you of any significant changes through your registered email address.
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
  name: 'PrivacyView'
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