<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Navbar from './layouts/Navbar.vue'
import Footer from './layouts/Footer.vue'


</script>

<template>
  <header v-if="$route.path !== '/' && $route.path !== '/login'">
    <Navbar />
  </header>
  <RouterView />
  <footer v-if="$route.path !== '/' && $route.path !== '/login'">
    <Footer />
  </footer>
</template>


<style scoped>

</style>
