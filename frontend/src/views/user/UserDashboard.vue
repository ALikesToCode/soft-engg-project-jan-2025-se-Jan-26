<script>
import SideNavBar from '@/layouts/SideNavBar.vue'
import ChatBotWrapper from '@/components/ChatBotWrapper.vue'
import api from '@/utils/api'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useToast } from 'vue-toastification'
export default {
  name: 'DashboardView',
  data() {
    return {
      isDataLoading: false,
      queryEmpty: true,
      showSplitScreen: false,
      recommendedMaterials: [
        // {
        //   id: 1,
        //   title: 'Advanced Python Programming',
        //   type: 'Course',
        //   progress: 0,
        //   thumbnail: 'https://placehold.co/100x100',
        //   reason: 'Based on your interest in Programming',
        // },
      ],
      personalizedRoadmaps: [
        {
          id: 1,
          title: 'Full Stack Development',
          progress: 45,
          totalSteps: 12,
          completedSteps: 5,
        },
        {
          id: 2,
          title: 'Data Structures & Algorithms',
          progress: 30,
          totalSteps: 10,
          completedSteps: 3,
        },
        {
          id: 3,
          title: 'Machine Learning Basics',
          progress: 20,
          totalSteps: 8,
          completedSteps: 2,
        },
        {
          id: 4,
          title: 'Software Engineering Practices',
          progress: 60,
          totalSteps: 15,
          completedSteps: 9,
        },
      ],
      bookmarkedMaterials: [
        // {
        //   id: 1,
        //   title: 'Design Patterns in Python',
        //   type: 'Article',
        //   author: 'Dr. Sarah Johnson',
        //   dateBookmarked: '2024-01-15',
        // },
      ],
      isDevelopment: import.meta.env.VITE_NODE_ENV === 'development',
    }
  },
  components: {
    SideNavBar,
    ChatBotWrapper,
    LoadingSpinner,
  },
  computed: {
    mainContentClass() {
      return {
        'md:grid-cols-2': !this.showSplitScreen,
        'md:grid-cols-3': this.showSplitScreen,
      }
    },
  },
  methods: {
    showSuccessToast(msg) {
      const toast = useToast() // Call inside the method
      toast.success(msg, { timeout: 3000 })
    },
    showErrorToast(error, defaultMessage) {
      const toast = useToast()
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    },
    startMaterial(material) {
      // TODO: Implement navigation to material
      console.log('Starting material:', material.title)
    },
    viewRoadmap(roadmap) {
      this.$router.push(`/user/roadmap/${roadmap.id}`)
    },
    removeBookmark(bookmark_id) {
      // TODO: Implement bookmark removal
      this.deleteBookMarkedMaterial(bookmark_id)
    },
    toggleSplitScreen() {
      this.showSplitScreen = !this.showSplitScreen
    },
    //API calls
    async getRecommendedCourses() {
      try {
        this.isDataLoading = true
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.get('/user/recommended-courses', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user data')
        console.log(response.data)
        this.recommendedMaterials = response.data
        this.showSuccessToast('Reccommended Courses fetched successfully')
      } catch (error) {
        this.showErrorToast(error, 'Failed to Load Recommended Courses')
        throw error
      } finally {
        this.isDataLoading = false
      }
    },

    async getBookMarkedMaterials() {
      try {
        this.isDataLoading = true
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.get('/user/bookmarked-materials', headers)
        if (response.status !== 200) throw new Error('Failed to fetch user data')
        console.log(response.data)
        this.bookmarkedMaterials = response.data
        this.showSuccessToast('Bookmarked Materials fetched successfully')
      } catch (error) {
        this.showErrorToast(error, 'Failed to Load Bookmarked Materials')
        throw error
      } finally {
        this.isDataLoading = false
      }
    },
    async deleteBookMarkedMaterial(bookmarkId) {
      try {
        this.isDataLoading = true
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.delete(`/user/bookmarked-materials/${bookmarkId}`, headers)
        if (response.status !== 200) {
          this.showErrorToast(error, 'Failed to delete the Bookmark')
          throw new Error('Failed to delete the data')
        }
        console.log(response.data)
        this.bookmarkedMaterials = response.data
        this.showSuccessToast('Bookmark Deleted Successfully')
      } catch (error) {
        this.showErrorToast(error, 'Failed to delete the Bookmark')
        throw error
      } finally {
        this.isDataLoading = false
      }
    },
  },

  mounted() {
    this.getRecommendedCourses(), this.getBookMarkedMaterials()
  },
}
</script>

<template>
  <div>
    <div class="flex h-screen">
      <div>
        <SideNavBar />
      </div>
      <div class="flex-1 p-6 overflow-y-auto bg-gray-50">
        <div class="max-w-7xl mx-auto">
          <!-- Recommended Section -->
          <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">Recommended for You</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              <div
                v-for="material in recommendedMaterials"
                :key="material.id"
                class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow"
              >
                <div class="flex items-start space-x-4">
                  <img
                    :src="material.thumbnail_path"
                    :alt="material.title"
                    class="w-16 h-16 rounded-lg object-cover"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between">
                      <div class="min-w-0">
                        <h3 class="font-semibold text-gray-800 truncate">{{ material.title }}</h3>
                        <span class="text-sm text-gray-500">{{ material.type }}</span>
                      </div>
                    </div>
                    <p class="text-sm text-gray-600 mt-2 line-clamp-2">{{ material.reason }}</p>
                    <button
                      @click="startMaterial(material)"
                      class="mt-3 text-sm text-maroon-600 hover:text-maroon-700 font-medium inline-flex items-center"
                    >
                      Start Learning
                      <span class="material-icons text-sm ml-1">arrow_forward</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="grid" :class="mainContentClass" gap-6>
            <!-- Personalized Roadmaps -->
            <div class="space-y-6">
              <h2 class="text-2xl font-bold text-gray-800">Your Learning Paths</h2>
              <div class="space-y-4">
                <div
                  v-for="roadmap in personalizedRoadmaps"
                  :key="roadmap.id"
                  class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow"
                >
                  <div class="flex items-center justify-between mb-2">
                    <h3 class="font-semibold text-gray-800 truncate">{{ roadmap.title }}</h3>
                    <span class="text-sm text-gray-500 whitespace-nowrap ml-2">
                      {{ roadmap.completedSteps }}/{{ roadmap.totalSteps }} steps
                    </span>
                  </div>
                  <div class="w-full bg-gray-100 rounded-full h-2">
                    <div
                      class="bg-maroon-600 h-2 rounded-full transition-all duration-500"
                      :style="{ width: `${roadmap.progress}%` }"
                    ></div>
                  </div>
                  <button
                    @click="viewRoadmap(roadmap)"
                    class="mt-3 text-sm text-maroon-600 hover:text-maroon-700 font-medium inline-flex items-center"
                  >
                    Continue Path
                    <span class="material-icons text-sm ml-1">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Bookmarked Materials -->
            <div class="space-y-6 sm:space-x-4">
              <h2 class="text-2xl font-bold text-gray-800 sm:ml-4">Bookmarked Materials</h2>
              <div class="space-y-4">
                <div
                  v-for="material in bookmarkedMaterials"
                  :key="material.id"
                  class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow group"
                >
                  <div class="flex items-start justify-between">
                    <div class="min-w-0 flex-1">
                      <h3 class="font-semibold text-gray-800 truncate">{{ material.title }}</h3>
                      <div class="flex items-center space-x-2 mt-1">
                        <span class="text-sm text-gray-500">{{ material.type }}</span>
                        <span class="text-gray-300">•</span>
                        <span class="text-sm text-gray-500 truncate">{{ material.author }}</span>
                      </div>
                      <div class="text-sm text-gray-500 mt-1">
                        Bookmarked on {{ new Date(material.date_bookmarked).toLocaleDateString() }}
                      </div>
                    </div>
                    <button
                      @click="removeBookmark(material.id)"
                      class="text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <span class="material-icons">bookmark_remove</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI Chatbot (Split Screen Mode) -->
            <div v-if="showSplitScreen" class="h-[calc(100vh-12rem)]">
              <ChatBotWrapper />
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Chat Bot (when not in split screen) -->
      <ChatBotWrapper v-if="!showSplitScreen" />
    </div>
  </div>
  <div v-if="isDataLoading" class="loading-overlay">
    <LoadingSpinner />
  </div>
</template>

<style scoped>
.material-icons {
  font-size: inherit;
  line-height: inherit;
  vertical-align: middle;
}

/* Smooth transitions */
.grid {
  transition: grid-template-columns 0.3s ease-in-out;
}

/* Improved scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}
</style>
