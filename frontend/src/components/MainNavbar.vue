<template>
  <BaseNavbar :show-logo="$route.name !== 'login'" :home-url="'/'">
    <template #nav-items>
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
    </template>
  </BaseNavbar>
</template>

<script>
import BaseNavbar from './BaseNavbar.vue'

export default {
  name: 'MainNavbar',
  components: {
    BaseNavbar
  }
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
