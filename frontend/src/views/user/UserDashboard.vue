<script>
import SideNavBar from '../../layouts/SideNavBar.vue';
import ChatBotBox from '../../components/ChatBotBox.vue'
export default {
  name: "DashboardView",
  data() {
    return {
      queryEmpty : true,
      }
    },
    components: {
      SideNavBar, 
      ChatBotBox
  },
};
</script>
<template>
    <div class="flex h-screen">
      <div>
        <SideNavBar />
      </div>
      <div class="flex-1 p-4 bg-gray-100">
        <div class="mt-4">
          <h2 class="text-lg font-semibold pt-4 pb-1">Recommended</h2>
          <div class="grid grid-cols-4 gap-4 mt-2">
            <div class="h-24 bg-white shadow rounded-lg"></div>
            <div class="h-24 bg-white shadow rounded-lg"></div>
            <div class="h-24 bg-white shadow rounded-lg"></div>
            <div class="h-24 bg-white shadow rounded-lg"></div>
          </div>
        </div>
        
        <div class="grid md:grid-cols-2 gap-6">
            <div class="">
                <div class="mt-4">
                    <h2 class="text-lg font-semibold pt-4 pb-1">Roadmaps</h2>
                    <div class="grid grid-cols-2 gap-4 mt-2">
                        <div class="h-12 bg-white shadow rounded-lg"></div>
                        <div class="h-12 bg-white shadow rounded-lg"></div>
                        <div class="h-12 bg-white shadow rounded-lg"></div>
                        <div class="h-12 bg-white shadow rounded-lg"></div>
                    </div>
                </div>
        
                <div class="mt-4">
                <h2 class="text-lg font-semibold pt-4 pb-1">Bookmarked</h2>
                <div class="grid grid-cols-2 gap-4 mt-2">
                    <div class="h-32 bg-white shadow rounded-lg"></div>
                    <div class="h-32 bg-white shadow rounded-lg"></div>
                </div>
                </div>
            </div>
            <div class="">
                <p class="text-center font-bold text-lg pt-4">AI Chatbot</p>
                <div class="h-full w-full bg-white shadow rounded p-1 m-4">
                  <ChatBotBox />
                </div>
            </div>
        </div>
      </div>
    </div>
  </template>
  
  <style scoped>
  </style>