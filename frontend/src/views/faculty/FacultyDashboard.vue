<template>
    <div class="flex items-start justify-center min-h-screen py-4 gap-4">
      <div class="w-2/3 max-w-2xl bg-white p-4 rounded shadow space-y-4">
        <div class="flex gap-4">
          <select v-model="selectedCourse" class="flex-1 px-4 py-2 bg-red-700 text-white rounded">
            <option disabled value="">Course</option>
            <option v-for="course in courses" :key="course">{{ course }}</option>
          </select>
  
          <select v-model="selectedMonth" class="flex-1 px-4 py-2 bg-red-700 text-white rounded">
            <option disabled value="">Month/Year</option>
            <option v-for="month in months" :key="month">{{ month }}</option>
          </select>
        </div>
        <br>
        <div class="space-y-4">
          <div class="p-4 border border-gray-300 rounded-lg bg-white shadow">
            Aggregated Insights (Common Student Engagement and Challenges)
          </div>
          <div class="p-4 border border-gray-300 rounded-lg bg-white shadow">
            Aggregated Insights (Frequently Accessed Topics)
          </div>
        </div>
      </div>
  
      <!-- Chatbot -->
      <div class="h-full w-1/3 max-w-md ml-6 bg-white p-1 rounded shadow">
        <h2 v-if="queryEmpty" class="text-center px-2 py-14">I am your AI assistant. Ask me...</h2>
        <ChatBotBox />
      </div>
    </div>
  </template>
  
  <script>
  import SideNavBar from '../../layouts/SideNavBar.vue';
  import ChatBotBox from '../../components/ChatBotBox.vue';
  
  export default {
    data() {
      return {
        courses: ["Math", "CT", "SE", "ST"],
        months: ["January 2025", "February 2025", "March 2025"],
        selectedCourse: "",
        selectedMonth: "",
        queryEmpty:true
      };
    },
    components: {
      SideNavBar, 
      ChatBotBox
    },
  };
  </script>
  
  <style scoped>
  </style>
  