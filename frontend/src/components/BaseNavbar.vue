<template>
  <header class="bg-white shadow-sm fixed w-full top-0 z-50">
    <div class="container mx-auto px-4 py-3 sm:py-4 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <div
          v-if="showLogo"
          class="w-8 h-8 sm:w-10 sm:h-10 bg-maroon-600 rounded-lg flex items-center justify-center"
        >
          <span class="material-icons text-white text-base sm:text-xl">school</span>
        </div>
        <router-link
          :to="homeUrl"
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
            <slot name="nav-items"></slot>
          </ul>
        </nav>
      </div>
    </div>
    <slot name="additional-content"></slot>
  </header>
</template>

<script>
export default {
  name: 'BaseNavbar',
  props: {
    homeUrl: {
      type: String,
      default: '/'
    },
    showLogo: {
      type: Boolean,
      default: true
    }
  },
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

.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
  font-size: 24px;
}
</style> 