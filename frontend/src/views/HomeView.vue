<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm fixed w-full top-0 z-50">
      <div class="container mx-auto px-4 py-3 sm:py-4 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <div
            class="w-8 h-8 sm:w-10 sm:h-10 bg-maroon-600 rounded-lg flex items-center justify-center"
          >
            <span class="material-icons text-white text-base sm:text-xl">school</span>
          </div>
          <div class="font-bold text-lg sm:text-xl text-maroon-600 truncate">Academic Guide</div>
        </div>

        <div class="relative">
          <button @click="toggleMenu" class="lg:hidden text-maroon-600 focus:outline-none p-2">
            <span class="material-icons">{{ isMenuOpen ? 'close' : 'menu' }}</span>
          </button>

          <nav
            :class="{ block: isMenuOpen, hidden: !isMenuOpen }"
            class="lg:flex items-center absolute lg:relative right-0 top-full lg:top-auto bg-white lg:bg-transparent shadow-lg lg:shadow-none rounded-lg lg:rounded-none p-4 lg:p-0 mt-2 lg:mt-0 w-48 lg:w-auto"
          >
            <ul class="flex flex-col lg:flex-row space-y-3 lg:space-y-0 lg:space-x-6">
              <li>
                <router-link
                  to="/"
                  class="text-gray-700 hover:text-maroon-600 font-medium hover:underline block py-1 px-2 rounded-md transition-colors duration-200"
                  >Home</router-link
                >
              </li>
              <li>
                <router-link
                  to="/about"
                  class="text-gray-700 hover:text-maroon-600 font-medium hover:underline block py-1 px-2 rounded-md transition-colors duration-200"
                  >About</router-link
                >
              </li>
              <li>
                <router-link
                  to="/contact"
                  class="text-gray-700 hover:text-maroon-600 font-medium hover:underline block py-1 px-2 rounded-md transition-colors duration-200"
                  >Contact</router-link
                >
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>

    <!-- Logout Message -->
    <div
      v-if="isLoggedOut"
      class="fixed top-16 sm:top-20 left-1/2 transform -translate-x-1/2 z-50 w-11/12 max-w-md mx-auto"
    >
      <div
        class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative"
        role="alert"
      >
        <span class="block sm:inline">You have been logged out successfully!</span>
        <button @click="dismissLogout" class="absolute top-0 bottom-0 right-0 px-4 py-3">
          <span class="material-icons text-green-500">close</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main class="flex-grow pt-16 sm:pt-20">
      <!-- Hero Section -->
      <div
        class="hero-section bg-gradient-to-br from-maroon-600 via-maroon-700 to-maroon-800 text-white py-12 sm:py-16 md:py-20"
      >
        <div class="container mx-auto px-4">
          <div class="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            <div class="space-y-6 sm:space-y-8 text-center lg:text-left">
              <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold leading-tight">
                Your Personal
                <span class="text-yellow-400 block sm:inline" style="color: #ffd700 !important"
                  >AI Academic Guide</span
                >
              </h1>
              <p class="text-base sm:text-lg text-gray-200 max-w-2xl mx-auto lg:mx-0">
                Enhance your learning journey in the IITM program with personalized AI assistance.
                Get smart recommendations, study strategies, and course guidance tailored just for
                you.
              </p>
              <div
                class="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 justify-center lg:justify-start"
              >
                <router-link
                  to="/login"
                  class="px-6 sm:px-8 py-3 border-2 border-white text-white font-semibold rounded-lg transform hover:scale-105 transition duration-200 flex items-center justify-center"
                >
                  <span class="material-icons mr-2 text-white hover:text-maroon-600">login</span>
                  <span class="text-white">Get Started</span>
                </router-link>
                <router-link
                  to="/about"
                  class="px-6 sm:px-8 py-3 border-2 border-white text-white font-semibold rounded-lg transform hover:scale-105 transition duration-200 flex items-center justify-center"
                >
                  <span class="material-icons mr-2 text-white hover:text-maroon-600">info</span>
                  <span class="text-white">Learn More</span>
                </router-link>
              </div>
            </div>
            <div class="hidden lg:flex justify-center items-center">
              <div class="relative w-full max-w-lg aspect-square">
                <!-- Main center icon -->
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="material-icons text-8xl text-white opacity-90">psychology</span>
                </div>

                <!-- Floating icons around the main icon -->
                <div class="absolute inset-0">
                  <!-- Top icons -->
                  <div
                    class="absolute top-0 left-1/2 -translate-x-1/2 transform -translate-y-4 flex items-center justify-center"
                  >
                    <span class="material-icons text-4xl text-yellow-400 animate-bounce"
                      >school</span
                    >
                  </div>

                  <!-- Right icons -->
                  <div class="absolute right-0 top-1/2 translate-x-4 -translate-y-1/2 transform">
                    <div class="space-y-8">
                      <span class="material-icons text-3xl text-white opacity-75 animate-pulse"
                        >auto_stories</span
                      >
                      <span
                        class="material-icons text-3xl text-white opacity-75 block animate-pulse"
                        style="animation-delay: 0.5s"
                        >tips_and_updates</span
                      >
                    </div>
                  </div>

                  <!-- Bottom icons -->
                  <div
                    class="absolute bottom-0 left-1/2 -translate-x-1/2 transform translate-y-4 flex space-x-8"
                  >
                    <span
                      class="material-icons text-3xl text-white opacity-75 animate-pulse"
                      style="animation-delay: 1s"
                      >schedule</span
                    >
                    <span
                      class="material-icons text-3xl text-white opacity-75 animate-pulse"
                      style="animation-delay: 1.5s"
                      >quiz</span
                    >
                  </div>

                  <!-- Left icons -->
                  <div class="absolute left-0 top-1/2 -translate-x-4 -translate-y-1/2 transform">
                    <div class="space-y-8">
                      <span
                        class="material-icons text-3xl text-white opacity-75 animate-pulse"
                        style="animation-delay: 2s"
                        >workspace_premium</span
                      >
                      <span
                        class="material-icons text-3xl text-white opacity-75 block animate-pulse"
                        style="animation-delay: 2.5s"
                        >history_edu</span
                      >
                    </div>
                  </div>

                  <!-- Floating circles background -->
                  <div class="absolute inset-0 opacity-20">
                    <div
                      class="absolute top-1/4 left-1/4 w-16 h-16 bg-yellow-400 rounded-full animate-ping"
                      style="animation-duration: 3s"
                    ></div>
                    <div
                      class="absolute bottom-1/4 right-1/4 w-12 h-12 bg-white rounded-full animate-ping"
                      style="animation-duration: 2.5s"
                    ></div>
                    <div
                      class="absolute top-1/3 right-1/3 w-8 h-8 bg-maroon-300 rounded-full animate-ping"
                      style="animation-duration: 2s"
                    ></div>
                  </div>
                </div>

                <!-- Rotating border effect -->
                <div
                  class="absolute inset-4 border-4 border-dashed border-white opacity-20 rounded-full animate-spin"
                  style="animation-duration: 20s"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Features Section -->
      <div class="py-12 sm:py-16 md:py-20 bg-white">
        <div class="container mx-auto px-4">
          <h2 class="text-2xl sm:text-3xl font-bold text-center text-gray-800 mb-8 sm:mb-12">
            Why Choose Our AI Guide?
          </h2>
          <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 max-w-7xl mx-auto">
            <div
              class="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition duration-200 flex flex-col items-center sm:items-start text-center sm:text-left"
            >
              <div class="w-12 h-12 bg-maroon-100 rounded-lg flex items-center justify-center mb-4">
                <span class="material-icons text-maroon-600">lightbulb</span>
              </div>
              <h3 class="text-xl font-semibold text-gray-800 mb-2">Smart Learning Strategies</h3>
              <p class="text-gray-600">
                Get personalized study techniques and time management tips based on your learning
                style.
              </p>
            </div>

            <div
              class="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition duration-200 flex flex-col items-center sm:items-start text-center sm:text-left"
            >
              <div class="w-12 h-12 bg-maroon-100 rounded-lg flex items-center justify-center mb-4">
                <span class="material-icons text-maroon-600">menu_book</span>
              </div>
              <h3 class="text-xl font-semibold text-gray-800 mb-2">Course Navigation</h3>
              <p class="text-gray-600">
                Easily find and access relevant course materials, assignments, and resources.
              </p>
            </div>

            <div
              class="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition duration-200 flex flex-col items-center sm:items-start text-center sm:text-left"
            >
              <div class="w-12 h-12 bg-maroon-100 rounded-lg flex items-center justify-center mb-4">
                <span class="material-icons text-maroon-600">verified_user</span>
              </div>
              <h3 class="text-xl font-semibold text-gray-800 mb-2">Academic Integrity</h3>
              <p class="text-gray-600">
                Maintain high ethical standards with our AI-powered plagiarism detection and
                citation tools.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      isMenuOpen: false,
      isLoggedOut: false,
    }
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
    },
    dismissLogout() {
      this.isLoggedOut = false
    },
  },
  mounted() {
    // Check if user was just logged out
    const logoutStatus = this.$route.query.logout
    if (logoutStatus === 'true') {
      this.isLoggedOut = true
      // Auto dismiss after 5 seconds
      setTimeout(() => {
        this.isLoggedOut = false
      }, 5000)
    }
  },
  watch: {
    // Close menu when route changes
    $route() {
      this.isMenuOpen = false
    },
  },
}
</script>

<style>
.router-link-active {
  @apply text-maroon-600 font-semibold;
}

/* Smooth scroll behavior */
html {
  scroll-behavior: smooth;
}

/* Fade-in animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

/* Mobile menu animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.block {
  animation: slideIn 0.3s ease-out forwards;
}

/* Custom animations for icons */
@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.float {
  animation: float 3s ease-in-out infinite;
}

@keyframes pulse-scale {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}

.pulse-scale {
  animation: pulse-scale 2s ease-in-out infinite;
}
</style>
