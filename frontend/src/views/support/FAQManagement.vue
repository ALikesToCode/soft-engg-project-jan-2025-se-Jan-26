<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Side Navigation -->
    <SideNavBar />

    <!-- Main Content -->
    <div class="flex-1 overflow-auto">
      <div class="min-h-screen bg-gray-50 py-8">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Header -->
          <div class="mb-8">
            <div class="flex justify-between items-center">
              <h1 class="text-3xl font-bold text-gray-900">FAQ Management</h1>
              <button
                @click="openCreateModal"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                Add New FAQ
              </button>
            </div>
          </div>

          <!-- Search and Filter -->
          <div class="mb-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Search -->
            <div>
              <label for="search" class="block text-sm font-medium text-gray-700">Search FAQs</label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <input
                  type="text"
                  id="search"
                  v-model="searchQuery"
                  @input="handleSearch($event.target.value)"
                  class="block w-full pr-10 sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Search questions or answers..."
                >
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Category Filter -->
            <div>
              <label for="category" class="block text-sm font-medium text-gray-700">Filter by Category</label>
              <select
                id="category"
                v-model="selectedCategory"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>

          <!-- FAQ List -->
          <div v-else class="bg-white shadow overflow-hidden sm:rounded-md">
            <ul v-if="filteredFaqs.length > 0" role="list" class="divide-y divide-gray-200">
              <li v-for="faq in filteredFaqs" :key="faq.id" class="px-6 py-4 hover:bg-gray-50">
                <div class="flex items-center justify-between">
                  <div class="flex-1 min-w-0 pr-4">
                    <h3 class="text-lg font-medium text-gray-900">{{ faq.question }}</h3>
                    <div class="mt-1 text-sm text-gray-600" v-html="faq.answer"></div>
                    <div class="mt-2 flex items-center text-sm text-gray-500">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {{ getCategoryName(faq.categoryId) }}
                      </span>
                      <span class="ml-4">Priority: {{ faq.priority || 0 }}</span>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <button
                      @click="editFaq(faq)"
                      class="p-2 text-blue-600 hover:text-blue-900"
                    >
                      <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                      </svg>
                    </button>
                    <button
                      @click="confirmDelete(faq)"
                      class="p-2 text-red-600 hover:text-red-900"
                    >
                      <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              </li>
            </ul>
            <div v-else class="px-6 py-12 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No FAQs found</h3>
              <p class="mt-1 text-sm text-gray-500">Get started by creating a new FAQ.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FAQ Edit/Create Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ editingFaq.id ? 'Edit FAQ' : 'Create New FAQ' }}
          </h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveFaq">
          <div class="space-y-4">
            <div>
              <label for="question" class="block text-sm font-medium text-gray-700">Question</label>
              <input
                type="text"
                id="question"
                v-model="editingFaq.question"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label for="answer" class="block text-sm font-medium text-gray-700">Answer</label>
              <textarea
                id="answer"
                v-model="editingFaq.answer"
                rows="4"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              ></textarea>
              <p class="mt-1 text-sm text-gray-500">HTML formatting is supported</p>
            </div>

            <div>
              <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
              <select
                id="category"
                v-model="editingFaq.categoryId"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option v-for="category in getCategories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <div>
              <label for="priority" class="block text-sm font-medium text-gray-700">Priority</label>
              <input
                type="number"
                id="priority"
                v-model="editingFaq.priority"
                min="0"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
              <p class="mt-1 text-sm text-gray-500">Higher numbers appear first in the list</p>
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {{ editingFaq.id ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useFaqStore } from '@/stores/faqStore'
import { useToast } from 'vue-toastification'
import { debounce } from 'lodash'
import SideNavBar from '@/layouts/SideNavBar.vue'

export default {
  name: 'FAQManagement',
  components: {
    SideNavBar
  },
  setup() {
    const faqStore = useFaqStore()
    const toast = useToast()

    const showModal = ref(false)
    const selectedCategory = ref('all')
    const loading = ref(false)
    const searchQuery = ref('')
    const editingFaq = ref({
      question: '',
      answer: '',
      categoryId: '',
      priority: 0
    })

    // Computed properties
    const categories = computed(() => faqStore.categories)
    const getCategories = computed(() => faqStore.getCategories)
    const filteredFaqs = computed(() => {
      let faqs = faqStore.getFaqsByCategory(selectedCategory.value)
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        faqs = faqs.filter(faq => 
          faq.question.toLowerCase().includes(query) ||
          faq.answer.toLowerCase().includes(query)
        )
      }
      return faqs
    })

    // Methods
    function getCategoryName(categoryId) {
      const category = categories.value.find(c => c.id === categoryId)
      return category ? category.name : 'Unknown'
    }

    function openCreateModal() {
      editingFaq.value = {
        question: '',
        answer: '',
        categoryId: getCategories.value[0].id,
        priority: 0
      }
      showModal.value = true
    }

    function editFaq(faq) {
      editingFaq.value = { ...faq }
      showModal.value = true
    }

    function closeModal() {
      if (confirm('Are you sure you want to close? Any unsaved changes will be lost.')) {
        showModal.value = false
        editingFaq.value = {
          question: '',
          answer: '',
          categoryId: '',
          priority: 0
        }
      }
    }

    async function saveFaq() {
      try {
        loading.value = true
        if (editingFaq.value.id) {
          await faqStore.updateFaq(editingFaq.value.id, editingFaq.value)
          toast.success('FAQ updated successfully')
        } else {
          await faqStore.createFaq(editingFaq.value)
          toast.success('FAQ created successfully')
        }
        showModal.value = false
        await faqStore.fetchFaqs()
      } catch (error) {
        toast.error(error.message || 'An error occurred while saving the FAQ')
      } finally {
        loading.value = false
      }
    }

    async function confirmDelete(faq) {
      if (confirm('Are you sure you want to delete this FAQ? This action cannot be undone.')) {
        try {
          await faqStore.deleteFaq(faq.id)
          toast.success('FAQ deleted successfully')
          await faqStore.fetchFaqs()
        } catch (error) {
          toast.error(error.message || 'An error occurred while deleting the FAQ')
        }
      }
    }

    // Search handler with debounce
    const handleSearch = debounce((value) => {
      searchQuery.value = value
    }, 300)

    // Watch for category changes
    watch(selectedCategory, () => {
      faqStore.fetchFaqs()
    })

    onMounted(async () => {
      try {
        loading.value = true
        await faqStore.fetchFaqs()
      } catch (error) {
        toast.error('Failed to load FAQs')
      } finally {
        loading.value = false
      }
    })

    return {
      showModal,
      selectedCategory,
      loading,
      searchQuery,
      editingFaq,
      categories,
      getCategories,
      filteredFaqs,
      getCategoryName,
      openCreateModal,
      editFaq,
      closeModal,
      saveFaq,
      confirmDelete,
      handleSearch
    }
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 