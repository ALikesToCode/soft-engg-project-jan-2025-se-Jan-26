<template>
  <div class="flex h-screen bg-gray-50">
    <SideNavBar />
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="mb-8 flex justify-between items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Course Content Management</h1>
            <p class="text-gray-800 mt-2">Create and manage your course materials</p>
          </div>
          <p
            @click="openAddCourseModal"
            class="bg-maroon-500 hover:bg-gra-600 px-4 py-2 text-gray-100 rounded cursor-pointer"
          >
            Add New Course +
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Course Selection & Module Management -->
          <div class="lg:col-span-1">
            <ModuleManager
              :courses="courses"
              @course-selected="handleCourseSelected"
              @module-selected="handleModuleSelected"
              @module-updated="handleModuleUpdated"
              @course-selected-data="handleCourseDataSelected"
              @lecture-data-content="handleLectureContentData"
            />
          </div>

          <!-- Content Upload & Preview -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Content Form -->
            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-lg font-semibold text-gray-900">Content Details</h2>

              <div class="space-y-4">
                <!-- Content Type Selection with Preview Toggle -->
                <div class="flex justify-between items-center">
                  <div class="flex-1 mr-4">
                    <label class="block text-sm font-medium text-gray-900 mb-1">Content Type</label>
                    <select
                      :disabled="isExistingData"
                      v-model="contentForm.type"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500"
                    >
                      <option value="lecture">Video Lecture</option>
                      <option value="document">Document</option>
                      <option value="quiz">Quiz</option>
                      <option value="assignment">Assignment</option>
                    </select>
                  </div>
                  <button
                    @click="togglePreview"
                    class="px-4 py-2 text-maroon-600 hover:bg-maroon-50 rounded-lg flex items-center gap-2"
                  >
                    <span class="material-icons">{{ previewMode ? 'visibility' : 'edit' }}</span>
                    {{ previewMode ? 'Preview' : 'Edit Mode' }}
                  </button>
                </div>

                <!-- Basic Content Form -->
                <div>
                  <label class="block text-sm font-medium text-gray-900 mb-1">Title</label>
                  <input
                    :disabled="!previewMode"
                    v-model="contentForm.title"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500"
                    placeholder="Enter content title"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-900 mb-1">Description</label>
                  <textarea
                    :disabled="!previewMode"
                    v-model="contentForm.description"
                    rows="3"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500"
                    placeholder="Add content description"
                  ></textarea>
                </div>

                <!-- Video URL Input -->
                <div v-if="contentForm.type === 'lecture'">
                  <label class="block text-sm font-medium text-gray-900 mb-1">Video URL</label>
                  <div class="relative">
                    <input
                      :disabled="!previewMode"
                      v-model="contentForm.videoUrl"
                      type="url"
                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 pr-12"
                      placeholder="https://youtube.com/..."
                    />
                    <span class="absolute right-3 top-2.5 text-gray-400">
                      <span class="material-icons">smart_display</span>
                    </span>
                  </div>
                </div>

                <!-- Document Upload -->
                <div v-if="contentForm.type === 'document'">
                  <label for="driveLink" class="block text-sm font-medium text-gray-900 mb-1"
                    >Google Drive Link for Document:</label
                  >
                  <input
                    :disabled="!previewMode"
                    id="driveLink"
                    v-model="driveLink"
                    type="url"
                    placeholder="Enter Google Drive link"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 pr-12"
                  />
                </div>

                <!-- Quiz Builder -->
                <div v-if="contentForm.type === 'quiz'">
                  <QuizBuilder :preview-mode="previewMode" @update:quiz="handleQuizUpdate" />
                </div>

                <!-- Assignment Builder -->
                <div v-if="contentForm.type === 'assignment'">
                  <AssignmentBuilder
                    :preview-mode="previewMode"
                    @update:assignment="handleAssignmentUpdate"
                  />
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex justify-between mt-6">
                <!-- <button
                  @click="saveAsDraft"
                  class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Save as Draft
                </button> -->
                <button
                  v-if="!isExistingData"
                  @click="publishContent"
                  class="px-6 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 hover:cursor-pointer"
                  :disabled="!isFormValid"
                >
                  Publish
                </button>
                <button
                  :disabled="!previewMode"
                  v-if="isExistingData"
                  @click="updatePublishedContent"
                  class="px-6 py-2 bg-maroon-600 text-white rounded-lg"
                  :class="{ 'hover:bg-maroon-700 hover:cursor-pointer': previewMode }"
                >
                  Update
                </button>
              </div>
            </div>

            <!-- Video Preview -->
            <div
              v-if="contentForm.type === 'lecture' && contentForm.videoUrl"
              class="bg-white rounded-lg shadow p-6"
            >
              <h2 class="text-lg font-semibold text-gray-900">Video Preview</h2>
              <div class="aspect-w-16">
                <iframe
                  :src="getEmbedUrl(contentForm.videoUrl)"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                  class="w-full h-full rounded-lg"
                ></iframe>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading || isSavingData" class="loading-overlay">
      <LoadingSpinner />
    </div>

    <!-- Confirm Dialog -->
    <ConfirmDialog
      v-if="showConfirmDialog"
      :message="confirmMessage"
      @confirm="confirmAction"
      @cancel="showConfirmDialog = false"
    />
    <!-- Add Course Modal -->
    <div
      v-if="showAddCourseModal"
      class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50 overflow-y-auto"
    >
      <div class="bg-white py-4 rounded-lg shadow-lg relative">
        <addCourse
          @close="closeAddCourseModal"
          @course-submitted="handleNewCourseDataSubmit"
          @course-code-error="handleCourseCodeError"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import SideNavBar from '@/layouts/SideNavBar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import ModuleManager from '@/components/content/ModuleManager.vue'
import FileUploader from '@/components/content/FileUploader.vue'
import QuizBuilder from '@/components/content/QuizBuilder.vue'
import AssignmentBuilder from '@/components/content/AssignmentBuilder.vue'
import { useContentStore } from '@/stores/contentStore'
import { useCourseStore } from '@/stores/courseStore'
import { useQuizStore } from '@/stores/quizStore'
import { useAssignmentStore } from '@/stores/assignmentStore'
import addCourse from './components/addCourse.vue'
import api from '@/utils/api'

export default {
  name: 'ContentUpload',
  components: {
    SideNavBar,
    LoadingSpinner,
    ConfirmDialog,
    ModuleManager,
    FileUploader,
    QuizBuilder,
    AssignmentBuilder,
    addCourse,
  },
  setup() {
    const toast = useToast()
    const contentStore = useContentStore()
    const courseStore = useCourseStore()
    const quizStore = useQuizStore()
    const assignmentStore = useAssignmentStore()

    // State Management
    const showAddCourseModal = ref(false)
    const isSavingData = ref(false)
    const isLoading = ref(false)
    const showConfirmDialog = ref(false)
    const confirmAction = ref(null)
    const confirmMessage = ref('')
    const unsavedChanges = ref(false)
    const selectedModule = ref(null)
    const previewMode = ref(false)
    const courses = ref([])
    const selectedCourseId = ref(null)
    const selectedWeek_ = ref(null)
    const selectedModuleId = ref(null)
    const selectedLectureId = ref(null)
    const isExistingData = ref(false)
    const driveLink = ref('')

    // Form State
    const contentForm = ref({
      title: '',
      description: '',
      type: 'lecture',
      videoUrl: '',
      status: 'draft',
      moduleId: null,
      order: 0,
      metadata: {
        duration: '',
        difficulty: 'intermediate',
        prerequisites: [],
        learningObjectives: [],
        visibility: 'hidden',
      },
    })

    // Computed Properties
    const isFormValid = computed(() => {
      if (!contentForm.value.title || !contentForm.value.description) return false
      if (!selectedModuleId.value) return false

      switch (contentForm.value.type) {
        case 'lecture':
          return isValidVideoUrl(contentForm.value.videoUrl)
        case 'document':
          return true //!!contentForm.value.file
        case 'quiz':
          return contentForm.value.questions?.length > 0
        case 'assignment':
          return contentForm.value.metadata?.dueDate && contentForm.value.metadata?.points > 0
        default:
          return false
      }
    })

    // Event Handlers
    const handleCourseDataSelected = ({ courseId, selectedWeek, moduleId }) => {
      isExistingData.value = false
      selectedCourseId.value = courseId
      selectedWeek_.value = selectedWeek
      selectedModuleId.value = moduleId
      contentForm.value = {
        title: '',
        description: '',
        type: 'lecture',
        videoUrl: '',
        status: 'draft',
        moduleId: null,
        order: 0,
        metadata: {
          duration: '',
          difficulty: 'intermediate',
          prerequisites: [],
          learningObjectives: [],
          visibility: 'hidden',
        },
      }
    }

    //New Course Data addition methods
    const openAddCourseModal = () => {
      showAddCourseModal.value = true
    }
    const closeAddCourseModal = () => {
      showAddCourseModal.value = false
    }

    const handleNewCourseDataSubmit = async (newCourseData) => {
      isSavingData.value = true
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }

        const response = await api.post(
          '/courses',
          {
            ...newCourseData,
          },
          headers,
        )
        if (response.status === 200) {
          toast.success('Course has been added successfully...')
        }
      } catch (err) {
        console.log(err)
        toast.error('Failed to add the course...')
      } finally {
        isSavingData.value = false
      }
    }

    const handleCourseCodeError = (msg) => {
      toast.error(msg)
    }

    const handleLectureContentData = (data) => {
      selectedLectureId.value = data.id
      isExistingData.value = data.isExistingData
      previewMode.value = false
      contentForm.value.title = data.lecture_title
      contentForm.value.videoUrl = data.content_url
      contentForm.value.description = data.content_desc

      contentForm.value.type = 'lecture' //when user has selected some other type
      if (data.file_type) {
        contentForm.value.type = data.file_type
      }
      if (data.driveLink) {
        driveLink.value = data.driveLink
      }
    }
    const handleCourseSelected = (courseId) => {
      contentForm.value.courseId = courseId
      selectedModule.value = null
    }

    const handleModuleSelected = (module) => {
      selectedModule.value = module
      contentForm.value.moduleId = module.id
    }

    const handleModuleUpdated = () => {
      toast.success('Module has been deleted!')
    }

    const handleFileSelected = (file) => {
      contentForm.value.file = file
    }

    const handleFileRemoved = () => {
      contentForm.value.file = null
    }

    const handleQuizUpdate = (quizData) => {
      contentForm.value.questions = quizData.questions
      contentForm.value.metadata = {
        ...contentForm.value.metadata,
        ...quizData.settings,
      }
    }

    const handleAssignmentUpdate = (assignmentData) => {
      contentForm.value.metadata = {
        ...contentForm.value.metadata,
        ...assignmentData.settings,
      }
      contentForm.value.file = assignmentData.file
    }

    // Actions
    const togglePreview = () => {
      previewMode.value = !previewMode.value
    }

    const saveAsDraft = async () => {
      try {
        contentForm.value.status = 'draft'
        await saveContent()
        toast.success('Content saved as draft')
      } catch (error) {
        handleError(error, 'Failed to save draft')
      }
    }

    const publishContent = async () => {
      if (!isFormValid.value) return

      showConfirmDialog.value = true
      confirmMessage.value =
        'Are you sure you want to publish this content? Published content will be immediately visible to students.'
      confirmAction.value = async () => {
        try {
          contentForm.value.status = 'published'
          showConfirmDialog.value = false
          isSavingData.value = true
          await saveContent()
          toast.success('Content published successfully')
          isSavingData.value = false
          resetForm()
        } catch (error) {
          handleError(error, 'Failed to publish content')
          showConfirmDialog.value = false
        } finally {
          showConfirmDialog.value = false
          isSavingData.value = false
        }
      }
    }

    const saveContent = async () => {
      isLoading.value = true
      try {
        const contentData = {
          ...contentForm.value,
          moduleId: selectedModuleId.value,
          courseId: selectedCourseId.value,
        }
        if (contentForm.value.type === 'quiz') {
          await quizStore.createQuiz(contentData)
        } else if (contentForm.value.type === 'assignment') {
          await assignmentStore.createAssignment(contentData)
        } else if (contentForm.value.type === 'document') {
          const url = '/courses/module/doc_content/lecture'
          await saveDocumentContent(contentData, url)
        } else {
          const url = '/courses/module/content/lecture' //for content type = video/lecture
          await contentStore.createContent(contentData, url)
        }
      } catch (error) {
        isLoading.value = false
        throw error
      } finally {
        isLoading.value = false
      }
    }

    const updatePublishedContent = async () => {
      console.log(contentForm.value)
      // if (!isFormValid.value) return
      showConfirmDialog.value = true
      confirmMessage.value =
        'Are you sure you want to update this content? Updated content will be immediately visible to students.'
      confirmAction.value = async () => {
        try {
          contentForm.value.status = 'updated'
          showConfirmDialog.value = false
          isSavingData.value = true
          console.log('type = ' + contentForm.value.type)
          if (contentForm.value.type === 'lecture') await updateContent()
          else if (contentForm.value.type === 'document') {
            console.log('Updating document')
            await updateDocumentContent()
          }
          toast.success('Content Updated successfully')
          isSavingData.value = false
          resetForm()
        } catch (error) {
          handleError(error, 'Failed to updated content')
          showConfirmDialog.value = false
        } finally {
          showConfirmDialog.value = false
          isSavingData.value = false
        }
      }
    }

    const updateContent = async () => {
      isLoading.value = true
      try {
        contentForm.value.moduleId = '0'
        const contentData = {
          ...contentForm.value,
          lectureId: selectedLectureId.value,
        }
        console.log({ ...contentData })
        const url = '/courses/module/content/lecture' //for content type = video/lecture
        await contentStore.updateContent(contentData, url)
      } catch (error) {
        isLoading.value = false
        throw error
      } finally {
        isLoading.value = false
      }
    }

    const saveDocumentContent = async (contentData, url) => {
      console.log('Uploading Document...')
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        const data = {
          ...contentData,
          driveDocLink: driveLink.value,
        }
        console.log(data)
        const response = await api.post(url, data, headers)
        console.log('Upload successful:', response.data)
        return response.data
      } catch (error) {
        console.error('Error uploading document:', error)
        throw error
      }
    }

    const updateDocumentContent = async () => {
      console.log('updating doc content')
      isLoading.value = true
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('No authentication token found')

        const headers = {
          headers: {
            Authorization: `Bearer ${token}`, // Add token to Authorization header
          },
        }
        contentForm.value.moduleId = '0'
        const contentData = {
          ...contentForm.value,
          driveDocLink: driveLink.value,
          lectureId: selectedLectureId.value,
        }
        console.log({ ...contentData })
        const url = '/courses/module/doc_content/lecture' //for content type = video/lecture
        const response = await api.put(url, contentData, headers)
      } catch (error) {
        isLoading.value = false
        throw error
      } finally {
        isLoading.value = false
      }
    }

    // Utility Functions
    const isValidVideoUrl = (url) => {
      return url?.match(/^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/)
    }

    const getEmbedUrl = (url) => {
      if (url.includes('youtube.com') || url.includes('youtu.be')) {
        const videoId = url.split('v=')[1] || url.split('/').pop()
        return `https://www.youtube.com/embed/${videoId}`
      }
      return url
    }

    const resetForm = () => {
      contentForm.value = {
        title: '',
        description: '',
        type: 'lecture',
        videoUrl: '',
        status: 'draft',
        moduleId: selectedModule.value?.id,
        order: 0,
        metadata: {
          duration: '',
          difficulty: 'intermediate',
          prerequisites: [],
          learningObjectives: [],
          visibility: 'hidden',
        },
      }
      unsavedChanges.value = false
    }

    const handleError = (error, defaultMessage) => {
      console.error(error)
      const message = error.response?.data?.message || defaultMessage
      toast.error(message)
    }

    // Lifecycle Hooks
    onMounted(async () => {
      try {
        isLoading.value = true
        const response = await courseStore.getFacultyCourses()
        courses.value = response.data
      } catch (error) {
        handleError(error, 'Failed to load courses')
      } finally {
        isLoading.value = false
      }
    })

    // Watch for Changes
    watch(
      [contentForm],
      () => {
        unsavedChanges.value = true
      },
      { deep: true },
    )

    return {
      isLoading,
      showConfirmDialog,
      confirmAction,
      confirmMessage,
      courses,
      contentForm,
      selectedModule,
      previewMode,
      isFormValid,
      handleCourseSelected,
      handleModuleSelected,
      handleModuleUpdated,
      handleFileSelected,
      handleFileRemoved,
      handleQuizUpdate,
      handleAssignmentUpdate,
      togglePreview,
      saveAsDraft,
      publishContent,
      getEmbedUrl,
      selectedCourseId,
      selectedModuleId,
      selectedWeek_,
      handleCourseDataSelected,
      isSavingData,
      handleLectureContentData,
      isExistingData,
      updatePublishedContent,
      selectedLectureId,
      driveLink,
      updateDocumentContent,
      //New Course Data addition
      showAddCourseModal,
      openAddCourseModal,
      closeAddCourseModal,
      handleNewCourseDataSubmit,
      handleCourseCodeError,
    }
  },
}
</script>

<style>
.aspect-w-16 {
  position: relative;
  padding-bottom: 56.25%;
}

.aspect-w-16 iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.loading-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.form-input {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 transition-all duration-200;
}

.form-label {
  @apply block text-sm font-medium text-gray-900 mb-1;
}

.preview-mode {
  @apply bg-gray-100 p-4 rounded-lg border border-gray-300;
}
</style>
