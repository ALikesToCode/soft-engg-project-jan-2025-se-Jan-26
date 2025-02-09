<template>
  <footer class="bg-gray-800 text-white py-8 sm:py-12">
    <div class="container mx-auto px-4">
      <div class="grid sm:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <div class="text-center sm:text-left">
          <h3 class="text-lg font-semibold mb-4">About IITM</h3>
          <p class="text-gray-400 text-sm">A Institution bringing world-class education to everyone.</p>
        </div>
        <div class="text-center sm:text-left">
          <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2 text-sm text-gray-400">
            <li>
              <router-link to="/faq" class="hover:text-white flex items-center justify-center sm:justify-start transition-colors duration-200">
                <span class="material-icons text-sm mr-2">help_outline</span>FAQ
              </router-link>
            </li>
            <li>
              <router-link to="/privacy-policy" class="hover:text-white flex items-center justify-center sm:justify-start transition-colors duration-200">
                <span class="material-icons text-sm mr-2">privacy_tip</span>Privacy Policy
              </router-link>
            </li>
            <li>
              <router-link to="/terms-of-service" class="hover:text-white flex items-center justify-center sm:justify-start transition-colors duration-200">
                <span class="material-icons text-sm mr-2">gavel</span>Terms of Service
              </router-link>
            </li>
          </ul>
        </div>
      </div>
      <div class="border-t border-gray-700 mt-8 pt-8 text-center text-xs sm:text-sm text-gray-400">
        © 2025 Software Engineering Project | SE Project Team 26 Jan Term 2025 | All rights reserved.
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'MainFooter'
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