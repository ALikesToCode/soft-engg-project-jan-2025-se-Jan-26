<script>
import MainNavbar from '@/components/MainNavbar.vue'
import MainFooter from '@/components/MainFooter.vue'

export default {
  name: 'App',
  components: {
    MainNavbar,
    MainFooter
  },
  computed: {
    showNavbar() {
      return !this.$route.meta.hideNavbar
    },
    showFooter() {
      return !this.$route.meta.hideFooter && this.$route.name !== 'login'
    }
  }
}
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <MainNavbar v-if="showNavbar" />
    <main class="flex-grow">
      <router-view />
    </main>
    <MainFooter v-if="showFooter" />
  </div>
</template>

<style>
@import './assets/main.css';

/* Base styles */
body {
  @apply bg-gray-50;
}

/* Transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
