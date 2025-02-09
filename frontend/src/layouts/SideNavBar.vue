<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="flex h-screen">
    <div
      class="w-16 bg-gradient-to-b from-red-800 to-red-600 flex flex-col justify-center items-center p-2 text-white space-y-3"
    >
      <div class="text-4xl">
        <router-link to="/user/dashboard">
          <span
            class="material-symbols-outlined"
            :class="{ 'text-yellow-400': route.path === '/user/dashboard' }"
          >
            dashboard
          </span>
        </router-link>
      </div>
      <div class="text-4xl">
        <router-link to="/user/courses">
          <span
            class="hover:cursor-pointer"
            :class="{ 'text-yellow-400': route.path === '/user/courses' }"
          >
            <span class="material-symbols-outlined">auto_stories</span>
          </span>
        </router-link>
      </div>
      <div class="text-4xl">
        <router-link to="/user/course-history">
          <span
            class="material-symbols-outlined"
            :class="{ 'text-yellow-400': route.path === '/user/history' }"
          >
            history
          </span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style>
.material-symbols-outlined {
  font-variation-settings:
    'FILL' 0,
    'wght' 400,
    'GRAD' 0,
    'opsz' 24;
  font-size: 32px; /* Icon size */
}
</style>
