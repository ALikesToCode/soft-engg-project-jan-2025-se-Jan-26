<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">Help & Support</h1>
          <!-- Add New FAQ Button for Support Staff -->
          <button v-if="isSupport"
                  @click="createNewFAQ"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add New FAQ
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- Search Bar -->
      <div class="mb-8">
        <div class="max-w-3xl mx-auto">
          <div class="relative">
            <input type="text" 
                   v-model="searchQuery" 
                   @input="handleSearch"
                   placeholder="Search for help topics..." 
                   class="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            <div class="absolute right-3 top-3 text-gray-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Tabs -->
      <div class="mb-8">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button v-for="category in categories" 
                    :key="category.id"
                    @click="currentCategory = category.id"
                    :class="[
                      currentCategory === category.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                      'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm'
                    ]">
              {{ category.name }}
            </button>
          </nav>
        </div>
      </div>

      <!-- FAQ Content -->
      <div class="space-y-6">
        <div v-if="loading" class="text-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p class="mt-4 text-gray-500">Loading FAQs...</p>
        </div>

        <div v-else-if="filteredFAQs.length === 0" class="text-center py-12">
          <p class="text-gray-500">No FAQs found. Try adjusting your search or category.</p>
        </div>

        <div v-else>
          <div v-for="faq in filteredFAQs" :key="faq.id" class="bg-white shadow rounded-lg overflow-hidden">
            <button @click="toggleFAQ(faq.id)" 
                    class="w-full px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-blue-500">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-medium text-gray-900">{{ faq.question }}</h3>
                <span class="ml-6 h-7 flex items-center">
                  <svg :class="[expandedFAQs.includes(faq.id) ? '-rotate-180' : 'rotate-0', 'h-6 w-6 transform']" 
                       xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </div>
            </button>
            <div v-show="expandedFAQs.includes(faq.id)" class="px-6 pb-4">
              <div class="prose max-w-none text-gray-500" v-html="faq.answer"></div>
              
              <!-- FAQ Rating -->
              <div class="mt-4 flex items-center justify-between border-t pt-4">
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-500">Was this helpful?</span>
                  <button @click="rateFAQ(faq.id, true)" 
                          class="text-green-600 hover:text-green-700">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                    </svg>
                  </button>
                  <button @click="rateFAQ(faq.id, false)"
                          class="text-red-600 hover:text-red-700">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018c.163 0 .326.02.485.06L17 4m-7 10v2a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 11v-9m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                    </svg>
                  </button>
                </div>
                <div v-if="isSupport" class="flex space-x-2">
                  <button @click="editFAQ(faq)" 
                          class="text-blue-600 hover:text-blue-700">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="deleteFAQ(faq.id)"
                          class="text-red-600 hover:text-red-700">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Support Section -->
      <div class="mt-12 bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Still Need Help?</h2>
          <p class="text-gray-500 mb-6">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <button @click="showSupportModal = true"
                  class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            Contact Support
          </button>
        </div>
      </div>

      <!-- Support Request Modal -->
      <div v-if="showSupportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg max-w-2xl w-full p-6">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-medium">Submit Support Request</h3>
            <button @click="showSupportModal = false" class="text-gray-400 hover:text-gray-500">
              <span class="sr-only">Close</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="submitSupportRequest" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Subject</label>
              <input type="text" v-model="supportRequest.subject" required
                     class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Category</label>
              <select v-model="supportRequest.category" required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                <option value="technical">Technical Issue</option>
                <option value="account">Account Related</option>
                <option value="course">Course Related</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Description</label>
              <textarea v-model="supportRequest.description" required rows="4"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="showSupportModal = false"
                      class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Submit Request
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- FAQ Edit Modal -->
      <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg max-w-2xl w-full p-6">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-medium">{{ editingFAQ.id ? 'Edit' : 'Create' }} FAQ</h3>
            <button @click="closeEditModal" class="text-gray-400 hover:text-gray-500">
              <span class="sr-only">Close</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveFAQ" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Question</label>
              <input type="text" v-model="editingFAQ.question" required
                     class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Answer</label>
              <div class="mt-1">
                <textarea v-model="editingFAQ.answer" required rows="6"
                          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
                <p class="mt-1 text-sm text-gray-500">
                  You can use HTML tags for formatting (e.g., &lt;b&gt;, &lt;i&gt;, &lt;ul&gt;, &lt;li&gt;)
                </p>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700">Category</label>
              <select v-model="editingFAQ.categoryId" required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                <option v-for="category in categories.filter(c => c.id !== 'all')" 
                        :key="category.id" 
                        :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Order Priority</label>
              <input type="number" v-model="editingFAQ.priority" min="0"
                     class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                     placeholder="Higher numbers appear first">
              <p class="mt-1 text-sm text-gray-500">
                Optional: Set display order priority (higher numbers appear first)
              </p>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeEditModal"
                      class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                {{ editingFAQ.id ? 'Update' : 'Create' }} FAQ
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import useAuthStore from '../stores/useAuthStore';
import faqService from '../services/faq.service';
import { debounce } from 'lodash';

export default {
  name: 'FAQView',
  setup() {
    const authStore = useAuthStore();
    const isSupport = computed(() => authStore.role === 'support');

    const loading = ref(false);
    const searchQuery = ref('');
    const currentCategory = ref('all');
    const expandedFAQs = ref([]);
    const showSupportModal = ref(false);
    const showEditModal = ref(false);

    const categories = ref([
      { id: 'all', name: 'All Topics' },
      { id: 'general', name: 'General' },
      { id: 'technical', name: 'Technical' },
      { id: 'courses', name: 'Courses' },
      { id: 'account', name: 'Account' },
      { id: 'faculty', name: 'Faculty' }
    ]);

    const faqs = ref([]);
    const editingFAQ = ref({
      question: '',
      answer: '',
      categoryId: '',
      priority: 0
    });

    const supportRequest = ref({
      subject: '',
      category: '',
      description: ''
    });

    const filteredFAQs = computed(() => {
      let filtered = faqs.value;
      
      if (currentCategory.value !== 'all') {
        filtered = filtered.filter(faq => faq.categoryId === currentCategory.value);
      }
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(faq => 
          faq.question.toLowerCase().includes(query) ||
          faq.answer.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    });

    const handleSearch = debounce(async () => {
      if (searchQuery.value.length >= 2) {
        loading.value = true;
        try {
          const results = await faqService.searchFaqs(searchQuery.value);
          faqs.value = results;
        } catch (error) {
          console.error('Search failed:', error);
          toast.error('Failed to search FAQs');
        } finally {
          loading.value = false;
        }
      } else if (searchQuery.value.length === 0) {
        // Reset to all FAQs when search is cleared
        loadFAQs();
      }
    }, 300);

    const toggleFAQ = (faqId) => {
      const index = expandedFAQs.value.indexOf(faqId);
      if (index === -1) {
        expandedFAQs.value.push(faqId);
      } else {
        expandedFAQs.value.splice(index, 1);
      }
    };

    const loadFAQs = async () => {
      loading.value = true;
      try {
        const response = await faqService.getAllFaqs();
        faqs.value = response;
      } catch (error) {
        console.error('Failed to load FAQs:', error);
      } finally {
        loading.value = false;
      }
    };

    const rateFAQ = async (faqId, isHelpful) => {
      try {
        await faqService.rateFAQ(faqId, isHelpful);
        // Optionally update the UI to show the rating was recorded
      } catch (error) {
        console.error('Failed to rate FAQ:', error);
      }
    };

    const submitSupportRequest = async () => {
      try {
        await faqService.submitSupportRequest(supportRequest.value);
        showSupportModal.value = false;
        supportRequest.value = { subject: '', category: '', description: '' };
        // Show success message
      } catch (error) {
        console.error('Failed to submit support request:', error);
        // Show error message
      }
    };

    const editFAQ = (faq) => {
      editingFAQ.value = { ...faq };
      showEditModal.value = true;
    };

    const createNewFAQ = () => {
      editingFAQ.value = {
        question: '',
        answer: '',
        categoryId: categories.value[1].id, // Default to first category after 'all'
        priority: 0
      };
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      if (confirm('Are you sure you want to close? Any unsaved changes will be lost.')) {
        showEditModal.value = false;
        editingFAQ.value = {
          question: '',
          answer: '',
          categoryId: '',
          priority: 0
        };
      }
    };

    const saveFAQ = async () => {
      try {
        loading.value = true;
        if (editingFAQ.value.id) {
          await faqService.updateFaq(editingFAQ.value.id, editingFAQ.value);
          toast.success('FAQ updated successfully');
        } else {
          await faqService.createFaq(editingFAQ.value);
          toast.success('FAQ created successfully');
        }
        showEditModal.value = false;
        await loadFAQs();
      } catch (error) {
        toast.error(error.message || 'An error occurred while saving the FAQ');
      } finally {
        loading.value = false;
      }
    };

    const deleteFAQ = async (faqId) => {
      if (confirm('Are you sure you want to delete this FAQ? This action cannot be undone.')) {
        try {
          await faqService.deleteFaq(faqId);
          toast.success('FAQ deleted successfully');
          await loadFAQs();
        } catch (error) {
          toast.error(error.message || 'An error occurred while deleting the FAQ');
        }
      }
    };

    onMounted(() => {
      loadFAQs();
    });

    return {
      loading,
      searchQuery,
      currentCategory,
      categories,
      faqs,
      filteredFAQs,
      expandedFAQs,
      showSupportModal,
      showEditModal,
      supportRequest,
      editingFAQ,
      isSupport,
      handleSearch,
      toggleFAQ,
      rateFAQ,
      submitSupportRequest,
      editFAQ,
      saveFAQ,
      deleteFAQ,
      createNewFAQ,
      closeEditModal
    };
  }
};
</script>

<style scoped>
.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Add smooth transition for modal */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>