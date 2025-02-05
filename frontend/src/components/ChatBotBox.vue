<template>
    <div class="flex flex-col h-full w-full pr-2 pt-2 pb-1 pl-1">
      <div class="flex-1 overflow-y-auto bg-white">
        <div v-for="(message, index) in messages" :key="index" class="mb-3">
          <div v-if="message.type === 'text'" class="flex">
            <div class="bg-gray-200 p-2 rounded-lg max-w-xs">
              <p class="text-sm">{{ message.content }}</p>
            </div>
          </div>
          <div v-if="message.type === 'image'" class="mt-2">
            <img :src="message.content" alt="Uploaded" class="w-40 rounded-lg" />
          </div>
        </div>
      </div>

      <div class="flex items-center bg-white py-2 px-1">
        <div class="relative flex-1">
            <input
            type="text"
            v-model="newMessage"
            placeholder="Type a message..."
            class="w-full p-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:border-red-700 focus:ring-1 focus:ring-red-700"
            @keyup.enter="sendMessage"
            />
          <label class="absolute inset-y-0 right-2 flex items-center cursor-pointer">
            <i class="text-xl text-gray-500 bi bi-cloud-arrow-up"></i>
            <input type="file" class="hidden" accept="image/*" @change="uploadImage" />
          </label>
        </div>
        
        &nbsp;
        <button @click="sendMessage" class="bg-red-700 text-white px-4 py-2 rounded hover:cursor-pointer hover:bg-red-800">
          <i class="bi bi-send-check"></i>
        </button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        messages: [], 
        newMessage: "", 
      };
    },
    methods: {
      sendMessage() {
        if (this.newMessage.trim() !== "") {
          this.messages.push({ type: "text", content: this.newMessage });
          this.newMessage = ""; // Clear input field
        }
      },
      uploadImage(event) {
        const file = event.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.messages.push({ type: "image", content: e.target.result });
          };
          reader.readAsDataURL(file);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  html, body, #app {
    height: 100%;
    margin: 0;
  }
  
  .flex-1 {
    min-height: 0;
  }
  </style>
  