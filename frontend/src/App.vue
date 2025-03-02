<script>
import MainNavbar from '@/components/MainNavbar.vue'
import MainFooter from '@/components/MainFooter.vue'
import UserNavBar from '@/components/UserNavBar.vue'
import GlobalChat from '@/components/GlobalChat.vue'
import NotificationToast from '@/components/NotificationToast.vue'

export default {
  name: 'App',
  components: {
    MainNavbar,
    UserNavBar,
    MainFooter,
    GlobalChat,
    NotificationToast
  },
  computed: {
    showNavbar() {
      return !this.$route.meta.hideNavbar
    },
    showFooter() {
      return !this.$route.meta.hideFooter && this.$route.name !== 'login'
    },
    showUserNavbar() {
      return !this.$route.meta.hideUserNavbar
    },
  },
}
</script>

<template>
  <div class="flex flex-col min-h-screen custom-scrollbar-light">
    <MainNavbar v-if="showNavbar" />
    <UserNavBar v-if="showUserNavbar" />
    <main class="flex-grow" :class="{ 'pt-16': showUserNavbar }">
      <NotificationToast />
      <router-view />
    </main>
    <MainFooter v-if="showFooter" />
    <GlobalChat />
  </div>
</template>

<style>
/* Import base styles first */
@import './assets/base.css';

/* Then import Tailwind */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Then import our custom styles to override Tailwind */
@import './assets/text-colors.css';
@import './assets/hero-styles.css';

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
