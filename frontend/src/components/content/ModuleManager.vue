<template>
  <div class="space-y-6">
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
        <button 
          @click="addNewModule"
          class="text-maroon-600 hover:text-maroon-700"
        >
          <span class="material-icons">add_circle</span> Add Module
        </button>
      </div>

      <div class="space-y-3">
        <div 
          v-for="module in modules" 
          :key="module.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
        >
          <div class="flex items-center">
            <span class="material-icons text-gray-400 mr-3 cursor-move">drag_indicator</span>
            <span class="text-gray-900">{{ module.title }}</span>
          </div>
          <div class="flex space-x-2">
            <button @click="editModule(module)" class="text-blue-600 hover:text-blue-700">
              <span class="material-icons">edit</span>
            </button>
            <button @click="deleteModule(module.id)" class="text-red-600 hover:text-red-700">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Module Edit Modal -->
    <div v-if="showModuleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">{{ editingModule ? 'Edit' : 'Add' }} Module</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-900 mb-1">Module Title</label>
            <input
              v-model="moduleForm.title"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter module title"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-900 mb-1">Description</label>
            <textarea
              v-model="moduleForm.description"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter module description"
            ></textarea>
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
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { useContentStore } from '@/stores/contentStore'

export default {
  name: 'ModuleManager',
  props: {
    courses: {
      type: Array,
      required: true
    }
  },
  emits: ['course-selected', 'module-selected', 'module-updated'],
  setup(props, { emit }) {
    const toast = useToast()
    const contentStore = useContentStore()
    
    const selectedCourse = ref('')
    const modules = ref([])
    const showModuleModal = ref(false)
    const editingModule = ref(null)
    const moduleForm = ref({
      title: '',
      description: '',
      order: 0
    })

    watch(() => selectedCourse.value, async (newValue) => {
      if (newValue) {
        await loadModules()
      }
    })

    const loadModules = async () => {
      if (!selectedCourse.value) return
      try {
        const response = await contentStore.getModules(selectedCourse.value)
        modules.value = response.data
      } catch (error) {
        handleError(error, 'Failed to load modules')
      }
    }

    const addNewModule = () => {
      editingModule.value = null
      moduleForm.value = { title: '', description: '', order: 0 }
      showModuleModal.value = true
    }

    const editModule = (module) => {
      editingModule.value = module
      moduleForm.value = { ...module }
      showModuleModal.value = true
    }

    const closeModuleModal = () => {
      showModuleModal.value = false
      editingModule.value = null
      moduleForm.value = { title: '', description: '', order: 0 }
    }

    const saveModule = async () => {
      if (!validateModuleForm()) return
      
      try {
        const moduleData = {
          ...moduleForm.value,
          courseId: selectedCourse.value
        }
        
        if (editingModule.value) {
          await contentStore.updateModule(editingModule.value.id, moduleData)
          toast.success('Module updated successfully')
        } else {
          await contentStore.createModule(moduleData)
          toast.success('Module created successfully')
        }
        
        await loadModules()
        closeModuleModal()
        emit('module-updated')
      } catch (error) {
        handleError(error, 'Failed to save module')
      }
    }

    const deleteModule = async (moduleId) => {
      if (confirm('Are you sure you want to delete this module?')) {
        try {
          await contentStore.deleteModule(moduleId)
          modules.value = modules.value.filter(m => m.id !== moduleId)
          emit('module-updated')
        } catch (error) {
          handleError(error, 'Failed to delete module')
        }
      }
    }

    const validateModuleForm = () => {
      if (!moduleForm.value.title.trim()) {
        toast.error('Module title is required')
        return false
      }
      return true
    }

    const handleError = (error, defaultMessage) => {
      console.error(error)
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    }

    return {
      selectedCourse,
      modules,
      showModuleModal,
      editingModule,
      moduleForm,
      addNewModule,
      editModule,
      closeModuleModal,
      saveModule,
      deleteModule
    }
  }
}
</script> 