<template>
  <div>
    <label class="block text-sm font-medium text-gray-900 mb-1">Upload File</label>
    <div
      @click="triggerFileUpload"
      @drop.prevent="handleFileDrop"
      @dragover.prevent
      class="border-2 border-dashed border-gray-300 p-6 text-center rounded-lg cursor-pointer hover:border-maroon-500 hover:bg-maroon-50 transition-colors"
    >
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        @change="handleFileSelect"
        :accept="acceptedFileTypes"
      />
      <div class="space-y-2">
        <span class="material-icons text-3xl text-gray-400">cloud_upload</span>
        <p class="text-sm text-gray-800">
          <span class="font-medium">Click to upload</span> or drag and drop
        </p>
        <p class="text-xs text-gray-700">
          {{ fileTypeMessage }}
        </p>
      </div>
    </div>
    <!-- File Preview -->
    <div v-if="selectedFile" class="mt-2 p-3 bg-gray-50 rounded-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="material-icons text-maroon-600">description</span>
          <span class="text-sm text-gray-900">{{ selectedFile.name }}</span>
        </div>
        <button @click="removeFile" class="text-red-600 hover:text-red-700">
          <span class="material-icons">close</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'FileUploader',
  props: {
    contentType: {
      type: String,
      required: true
    }
  },
  emits: ['file-selected', 'file-removed'],
  setup(props, { emit }) {
    const fileInput = ref(null)
    const selectedFile = ref(null)

    const acceptedFileTypes = computed(() => {
      if (props.contentType === 'document') return '.pdf,.doc,.docx,.ppt,.pptx'
      if (props.contentType === 'assignment') return '.pdf,.doc,.docx,.zip'
      return ''
    })

    const fileTypeMessage = computed(() => {
      if (props.contentType === 'document') return 'PDF, DOC, DOCX, PPT, PPTX (max 50MB)'
      if (props.contentType === 'assignment') return 'PDF, DOC, DOCX, ZIP (max 50MB)'
      return ''
    })

    const triggerFileUpload = () => {
      fileInput.value.click()
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        emit('file-selected', file)
      }
    }

    const handleFileDrop = (event) => {
      const file = event.dataTransfer.files[0]
      if (file) {
        selectedFile.value = file
        emit('file-selected', file)
      }
    }

    const removeFile = () => {
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
      emit('file-removed')
    }

    return {
      fileInput,
      selectedFile,
      acceptedFileTypes,
      fileTypeMessage,
      triggerFileUpload,
      handleFileSelect,
      handleFileDrop,
      removeFile
    }
  }
}
</script> 