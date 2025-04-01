<template>
  <div class="space-y-6" @click="closeDropdown">
    <!-- Course Selection -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900">Course Selection</h2>
      <select
        v-model="selectedCourse"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500"
        @change="$emit('course-selected', selectedCourse)"
      >
        <option value="">Select a course</option>
        <option v-for="course in courses" :key="course.id" :value="course.id">
          {{ course.name }}
        </option>
      </select>
    </div>

    <!-- Module Management -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900">Modules</h2>
        <button @click="addNewModule" class="text-maroon-600 hover:text-maroon-700">
          <span class="material-icons">add_circle</span> Add Module
        </button>
      </div>

      <div class="space-y-3">
        <div
          v-for="module in modules"
          :key="module.id"
          class="relative flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
          @click.stop="toggleDropdown(module.id)"
        >
          <div @click="fetchModuleLectures(module.id)" class="flex items-center">
            <span class="material-icons text-gray-400 mr-3 cursor-move">drag_indicator</span>
            <div class="flex flex-col">
              <span class="text-gray-900">{{ module.title }}</span>
              <span class="text-xs text-gray-600 flex items-center">
                View Content
                <span class="material-symbols-outlined text-base ml-1">keyboard_arrow_down</span>
              </span>
            </div>
          </div>
          <div class="flex space-x-2">
            <button @click.stop="editModule(module)" class="text-blue-600 hover:text-blue-700">
              <span class="material-icons">edit</span>
            </button>
            <button @click.stop="deleteModule(module.id)" class="text-red-600 hover:text-red-700">
              <span class="material-icons">delete</span>
            </button>
          </div>
          <!-- Lecture List Dropdown Menu -->
          <div
            v-if="activeDropdown === module.id"
            class="absolute top-full left-0 mt-1 w-48 bg-white shadow-lg rounded-lg p-2 z-50"
          >
            <button
              @click="fetchLectureContentData(lecture.id)"
              v-for="lecture in lectures"
              :key="lecture.id"
              class="block w-full text-left px-4 py-2 hover:bg-gray-100"
            >
              <span>{{ lecture.content_type + ' ' }}</span>
              <span>{{ lecture.lecture_number }}</span>
            </button>
            <button
              v-if="!loadingLectureData"
              @click="sendDataToParent(module.id)"
              class="block w-full text-left px-4 py-2 hover:bg-gray-100"
            >
              Add Content +
            </button>
            <miniLoader v-if="loadingLectureData">Fetching Data...</miniLoader>
          </div>
        </div>
        <div v-if="modules.length === 0" class="px-2 py-4 flex justify-center items-center">
          <span
            v-if="!loadingModuleData"
            class="material-symbols-outlined text-yellow-500 text-2xl font-bold mr-1"
            >info</span
          >
          <p v-if="selectedCourse && !loadingModuleData">No Module is added yet. Add one...</p>
          <p v-if="!selectedCourse">Select a course to see the modules</p>
        </div>
        <miniLoader v-if="loadingModuleData">Fetching Data...</miniLoader>
      </div>
    </div>

    <!-- Module Edit Modal -->
    <div v-if="showModuleModal" class="modal-overlay">
      <div class="modal-content">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">
          {{ editingModule ? 'Edit' : 'Add' }} Module
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-900 mb-1">Week </label>
            <input
              v-model="moduleForm.week"
              type="number"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter Week"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-900 mb-1">Lecture</label>
            <input
              type="number"
              v-model="moduleForm.lecture"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter Lecture number"
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="closeModuleModal"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              @click="saveModule"
              class="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700"
            >
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
    <div>
      <miniLoader v-if="isDataLoading" class="loading-overlay"> Fetching data... </miniLoader>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { useContentStore } from '@/stores/contentStore'
import api from '@/utils/api'
import miniLoader from '../common/miniLoader.vue'
import LoadingSpinnerVue from '../common/LoadingSpinner.vue'

export default {
  name: 'ModuleManager',
  props: {
    courses: Array,
  },
  components: {
    miniLoader,
    LoadingSpinnerVue,
  },
  emits: [
    'course-selected',
    'module-selected',
    'module-updated',
    'course-selected-data',
    'lecture-data-content',
  ],
  setup(props, { emit }) {
    const toast = useToast()
    const contentStore = useContentStore()

    const selectedCourse = ref('')
    const modules = ref([])
    const lectures = ref([])
    const courseId = ref(null)
    const activeDropdown = ref(null)
    const showModuleModal = ref(false)
    const editingModule = ref(null)
    const loadingModuleData = ref(false)
    const loadingLectureData = ref(false)

    const selectedWeek = ref('')
    const selectedLecture = ref('')
    const isDataLoading = ref(false)

    const moduleForm = ref({
      week: '',
      lecture: '',
      order: 0,
    })

    watch(
      () => selectedCourse.value,
      async (newValue) => {
        if (newValue) {
          courseId.value = newValue
          modules.value = [] //to not show when changing selected course
          await loadModules()
        }
      },
    )

    const loadModules = async () => {
      if (!selectedCourse.value) return
      try {
        loadingModuleData.value = true
        const response = await contentStore.getModules(courseId.value)
        loadingModuleData.value = false
        modules.value = response.data
      } catch (error) {
        handleError(error, 'Failed to load modules')
      } finally {
        loadingModuleData.value = false
      }
    }

    const fetchModuleContent = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        const response = await api.get(`courses/module/${courseId}`, headers)
        modules.value = response.data
        return response
      } catch (error) {
        handleError(error, 'Failed to fetch module content')
      }
    }

    //FETCHES LECTURES FOR EACH MODULE
    const fetchModuleLectures = async (moduleId) => {
      try {
        modules.value.forEach((e) => {
          if (e.id === moduleId) {
            selectedWeek.value = e.position
          }
        })

        loadingLectureData.value = true
        lectures.value = []

        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.get(`courses/module/lecture/${moduleId}`, headers)
        loadingLectureData.value = false
        lectures.value = response.data
        return response
      } catch (error) {
        lectures.value = []
        handleError(error, 'Failed to fetch module lectures')
      } finally {
        loadingLectureData.value = false
      }
    }

    const fetchLectureContentData = async (lectureId) => {
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        isDataLoading.value = true
        const response = await api.get(`courses/lecture/content/${lectureId}`, headers)
        isDataLoading.value = false
        console.log(response.data)
        emit('lecture-data-content', { isExistingData: true, ...response.data })
      } catch (error) {
        isDataLoading.value = false
        handleError(error, 'Failed to fetch the lecture content')
      } finally {
        isDataLoading.value = false
      }
    }

    const addNewModule = () => {
      editingModule.value = null
      moduleForm.value = { week: '', lecture: '', order: 0 }
      showModuleModal.value = true
    }

    const editModule = (module) => {
      editingModule.value = module
      moduleForm.value = { ...module }
      showModuleModal.value = true
    }

    const toggleDropdown = (moduleId) => {
      activeDropdown.value = activeDropdown.value === moduleId ? null : moduleId
    }

    const closeDropdown = () => {
      activeDropdown.value = null
    }

    const closeModuleModal = () => {
      showModuleModal.value = false
      editingModule.value = null
      moduleForm.value = { week: '', lecture: '', order: 0 }
    }

    const saveModule = async () => {
      if (!validateModuleForm()) return
      try {
        const moduleData = {
          course_id: courseId.value,
          title: 'Week ' + moduleForm.value.week,
          position: moduleForm.value.week,
        }
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.post(
          '/courses/module',
          {
            ...moduleData,
          },
          headers,
        )
        await loadModules()
        closeModuleModal()
      } catch (error) {
        handleError(error, 'Failed to save module')
      }
    }

    const validateModuleForm = () => {
      if (!moduleForm.value.week || !moduleForm.value.lecture) {
        toast.error('Week and Lecture are required')
        return false
      }
      return true
    }

    const deleteModule = async (moduleId) => {
      if (confirm('Are you sure you want to delete this module?')) {
        try {
          await contentStore.deleteModule(moduleId)
          modules.value = modules.value.filter((m) => m.id !== moduleId)
          await loadModules()
          emit('module-updated')
        } catch (error) {
          handleError(error, 'Failed to delete module')
        }
      }
    }

    const handleError = (error, defaultMessage) => {
      console.error(error)
      toast.error(error.response?.data?.message || defaultMessage)
    }

    const sendDataToParent = (moduleId) => {
      // Emit values to the parent
      emit('course-selected-data', {
        courseId: courseId.value,
        selectedWeek: null,
        moduleId: moduleId,
      })
    }

    return {
      selectedCourse,
      modules,
      showModuleModal,
      editingModule,
      moduleForm,
      addNewModule,
      closeModuleModal,
      saveModule,
      activeDropdown,
      fetchModuleContent,
      editModule,
      deleteModule,
      toggleDropdown,
      closeDropdown,
      lectures,
      fetchModuleLectures,
      loadingModuleData,
      loadingLectureData,
      selectedWeek,
      selectedLecture,
      sendDataToParent,
      fetchLectureContentData,
      isDataLoading,
    }
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  max-width: 400px;
  width: 100%;
  position: relative;
  z-index: 50;
}
.dropdown-menu {
  position: absolute;
  background-color: white;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 200px;
  z-index: 10;
}
.loading-overlay {
  @apply fixed inset-auto top-24 left-1/2 -translate-x-1/2 py-5 px-12 rounded-md bg-gray-100 shadow-md;
}
</style>
