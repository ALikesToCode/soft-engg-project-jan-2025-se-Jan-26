<template>
  <div class="flex flex-col h-full w-full p-2">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto mb-3 space-y-4 pr-2">
      <!-- Message Bubbles -->
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        class="flex"
        :class="message.sender === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div class="max-w-[85%] flex flex-col space-y-1">
          <div 
            :class="[
              message.sender === 'user' 
                ? 'bg-maroon-600 text-white' 
                : 'bg-gray-100 text-gray-800',
              message.type === 'image' ? 'p-1' : 'p-3'
            ]"
            class="rounded-xl transition-all duration-200"
          >
            <!-- Text Message -->
            <p v-if="message.type === 'text'" class="text-sm leading-5">
              {{ message.content }}
            </p>
            
            <!-- Image Message -->
            <img 
              v-if="message.type === 'image'"
              :src="message.content" 
              alt="Uploaded content"
              class="w-48 h-32 object-cover rounded-lg"
            />
          </div>
          
          <!-- Timestamp -->
          <span 
            class="text-xs text-gray-500 px-2"
            :class="message.sender === 'user' ? 'text-right' : 'text-left'"
          >
            {{ message.timestamp }}
          </span>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="flex items-center space-x-2 bg-white p-2 rounded-lg shadow-sm border border-gray-200">
      <!-- File Upload -->
      <label class="cursor-pointer p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
        <span class="material-symbols-outlined text-gray-600 text-xl">image</span>
        <input 
          type="file" 
          class="hidden" 
          accept="image/*" 
          @change="uploadImage"
        />
      </label>

      <!-- Message Input -->
      <input
        type="text"
        v-model="newMessage"
        placeholder="Ask me anything..."
        class="flex-1 p-2 focus:outline-none placeholder-gray-400 text-sm"
        @keyup.enter="sendMessage"
      />

      <!-- Send Button -->
      <button
        @click="sendMessage"
        class="p-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 transition-colors"
        :disabled="!newMessage.trim()"
        aria-label="Send message"
      >
        <span class="material-symbols-outlined text-xl">send</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      messages: [],
      newMessage: '',
    }
  },
  watch: {
    messages() {
      this.$nextTick(this.scrollToBottom);
    }
  },
  methods: {
    sendMessage() {
      if (this.newMessage.trim()) {
        const message = {
          type: 'text',
          content: this.newMessage.trim(),
          sender: 'user',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        this.messages.push(message);
        this.newMessage = '';
        
        // Add temporary bot response (replace with actual API call)
        setTimeout(() => {
          this.messages.push({
            type: 'text',
            content: "This is a sample response from the AI assistant. Real implementation would connect to an AI API.",
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          });
        }, 1000);
      }
    },
    uploadImage(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.messages.push({
            type: 'image',
            content: e.target.result,
            sender: 'user',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          });
        };
        reader.readAsDataURL(file);
      }
    },
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.flex-1::-webkit-scrollbar {
  width: 6px;
}

.flex-1::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.flex-1::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.flex-1::-webkit-scrollbar-thumb:hover {
  background: #666;
}
</style>
