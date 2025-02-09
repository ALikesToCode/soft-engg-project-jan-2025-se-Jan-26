<template>
  <header class="bg-white shadow-sm fixed w-full top-0 z-50">
    <div class="container mx-auto px-4 py-3 sm:py-4 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <div
          :class="{ hidden: $route.name === 'login' }"
          class="w-8 h-8 sm:w-10 sm:h-10 bg-maroon-600 rounded-lg flex items-center justify-center"
        >
          <span class="material-icons text-white text-base sm:text-xl">school</span>
        </div>
        <router-link
          :class="{ hidden: $route.name === 'login' }"
          to="/"
          class="font-bold text-lg sm:text-xl text-maroon-600 hover:text-maroon-700 transition-colors duration-200"
        >
          Academic Guide
        </router-link>
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
                :class="{ 'text-maroon-600 font-semibold': $route.name === 'home' }"
              >
                Home
              </router-link>
            </li>
            <li>
              <router-link
                to="/about"
                class="text-gray-700 hover:text-maroon-600 font-medium hover:underline block py-1 px-2 rounded-md transition-colors duration-200"
                :class="{ 'text-maroon-600 font-semibold': $route.name === 'about' }"
              >
                About
              </router-link>
            </li>
            <li>
              <router-link
                to="/contact"
                class="text-gray-700 hover:text-maroon-600 font-medium hover:underline block py-1 px-2 rounded-md transition-colors duration-200"
                :class="{ 'text-maroon-600 font-semibold': $route.name === 'contact' }"
              >
                Contact
              </router-link>
            </li>
            <li>
              <router-link
                to="/login"
                class="text-gray-700 hover:text-maroon-600 font-medium hover:underline block py-1 px-2 rounded-md transition-colors duration-200"
                :class="{ 'text-maroon-600 font-semibold': $route.name === 'login' }"
              >
                Login
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'MainNavbar',
  data() {
    return {
      isMenuOpen: false,
    }
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
    },
  },
  watch: {
    $route() {
      this.isMenuOpen = false
    },
  },
}
</script>

<style scoped>
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
</style>
