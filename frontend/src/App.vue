<script>
import MainNavbar from '@/components/MainNavbar.vue'
import MainFooter from '@/components/MainFooter.vue'
import UserNavBar from '@/components/UserNavBar.vue'
import GlobalChat from '@/components/GlobalChat.vue'
import NotificationToast from '@/components/NotificationToast.vue'
import { useChatStore } from '@/stores/useChatStore'
import useAuthStore from '@/stores/useAuthStore'
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  components: {
    MainNavbar,
    UserNavBar,
    MainFooter,
    GlobalChat,
    NotificationToast
  },
  setup() {
    const chatStore = useChatStore()
    const authStore = useAuthStore()
    const route = useRoute()
    const isAuthInitialized = ref(false)
    
    // Check if current route is a public route
    const isPublicRoute = computed(() => {
      const publicRoutes = ['/', '/login', '/register', '/forgot-password', 
                          '/reset-password', '/auth-callback', '/about', 
                          '/contact', '/help', '/faq'];
      return publicRoutes.includes(route.path);
    });
    
    // Check if we should show the chat component
    const shouldShowChat = computed(() => {
      return authStore.token && !isPublicRoute.value;
    });
    
    onMounted(async () => {
      console.log("App mounted, initializing stores")
      
      // Initialize auth store first
      try {
        await authStore.initialize()
        isAuthInitialized.value = true
        console.log("Auth store initialized successfully")
      } catch (error) {
        console.error("Error initializing auth store:", error)
      }
      
      // Initialize chat store to load chat history from backend
      // Do this after auth is initialized since it depends on auth state
      chatStore.initialize()
    })
    
    return {
      chatStore,
      authStore,
      isAuthInitialized,
      isPublicRoute,
      shouldShowChat
    }
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
/* Import all CSS files first */
@import './assets/base.css';
@import './assets/text-colors.css';
@import './assets/hero-styles.css';

/* Then import Tailwind */
@tailwind base;
@tailwind components;
@tailwind utilities;

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
