<template>
  <div class="min-h-screen bg-gray-50 pt-16 sm:pt-20">
    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-maroon-600 via-maroon-700 to-maroon-800 text-white py-12">
      <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Frequently Asked Questions
          </h1>
          <p class="text-xl text-gray-200">
            Find answers to common questions about AI Academic Guide
          </p>
        </div>
      </div>
    </div>

    <!-- FAQ Section -->
    <div class="py-12 bg-white">
      <div class="container mx-auto px-4">
        <div class="max-w-3xl mx-auto">
          <div class="space-y-6">
            <div v-for="(faq, index) in faqs" :key="index" class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2 flex items-start">
                <span class="material-icons text-maroon-600 mr-2 flex-shrink-0">help_outline</span>
                {{ faq.question }}
              </h3>
              <p class="text-gray-600 ml-8">{{ faq.answer }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FAQView',
  data() {
    return {
      faqs: [
        {
          question: 'What is AI Academic Guide?',
          answer: 'AI Academic Guide is an intelligent learning assistant designed specifically for IITM BS students to enhance their academic journey through personalized support and guidance.'
        },
        {
          question: 'How can AI Academic Guide help me?',
          answer: 'Our platform provides personalized study strategies, course navigation assistance, and academic integrity tools to help you succeed in your IITM BS program.'
        },
        {
          question: 'Is the service free for IITM BS students?',
          answer: 'Yes, AI Academic Guide is completely free for all enrolled IITM BS students.'
        },
        {
          question: 'How do I get started?',
          answer: 'Simply sign up using your IITM BS credentials through our login page, and you\'ll have immediate access to all features.'
        }
      ]
    }
  }
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