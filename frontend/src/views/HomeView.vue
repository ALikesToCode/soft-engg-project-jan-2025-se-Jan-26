<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-white shadow">
      <div class="container mx-auto px-4 py-4 flex justify-between items-center">
        <div class="font-bold text-xl text-maroon-700">Software Engineering Project | IIT Madras BS</div>
        <div>
          <button @click="toggleMenu" class="lg:hidden text-maroon-700 focus:outline-none">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
        
        <nav :class="{'block': isMenuOpen, 'hidden': !isMenuOpen}" class="lg:flex flex-grow items-center justify-between space-x-6 float-right">
            <ul class="flex">
            <li><router-link to="/" class="text-gray-700 hover:text-maroon-600 pr-2 hover:underline">Home</router-link></li>
            <li><router-link to="/about" class="text-gray-700 hover:text-maroon-600 pr-2 hover:underline">About</router-link></li>
            <li><router-link to="/contact" class="text-gray-700 hover:text-maroon-600 hover:underline">Contact</router-link></li>
          </ul>
        </nav>
        </div>
      </div>
    </header>

    <div v-if="isLoggedOut" class="text-center py-6">
      <p class="text-green-600 text-lg">You have been logged out successfully!!</p>
    </div>
    <main class="flex-grow bg-gradient-to-r from-maroon-600 to-maroon-800 flex items-center justify-center py-12">
      <div class="bg-white p-8 rounded-2xl shadow-lg w-4/5 md:w-2/3 lg:w-1/2 text-center">
        <h1 class="text-4xl font-bold pb-6 text-gray-700">AI Agent for Academic Guidance</h1>
        <p class="text-gray-600 text-sm mb-6">
          Welcome to the AI Agent for Academic Guidance, designed to enhance the learning experience for students in the IITM BS program.
          The agent helps navigate course materials, improve study habits, and maintain academic integrity.
        </p>
        <p class="text-gray-600 text-sm mb-6">
          The agent suggests learning strategies, provides relevant resources, and guides students to course content.
          It supports multiple courses dynamically, ensuring personalized assistance.
        </p>
        <br>
        <router-link
          to="/login"
          class="w-full inline-block text-center py-3 px-6 bg-maroon-600 text-white font-semibold rounded-md shadow-md hover:bg-maroon-700 transition duration-200"
        >
          Take me to Login
        </router-link>
      </div>
    </main>

    <footer class="bg-gray-800 text-white py-4">
      <div class="container mx-auto px-4 text-center">
        Software Engineering Project 2025
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: "HomePage",
  data() {
    return {
      isMenuOpen: false,
    };
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
    }
  },
  computed: {
    isLoggedOut() {
      return this.$route.query.logout === 'true';
    }
  }
};
</script>

<style scoped>

.text-maroon-700 {
  color: #800000;
}
.bg-maroon-600 {
  background-color: #800000;
}
.bg-maroon-700 {
  background-color: #6a0000;
}
</style>
