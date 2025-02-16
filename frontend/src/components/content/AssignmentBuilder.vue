<template>
  <div class="space-y-6">
    <!-- Assignment Settings -->
    <div class="form-section">
      <h3 class="text-lg font-medium text-gray-900">Assignment Settings</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="form-label">Due Date</label>
          <input
            v-model="assignmentSettings.dueDate"
            type="datetime-local"
            class="form-input"
          />
        </div>
        <div>
          <label class="form-label">Points</label>
          <input
            v-model.number="assignmentSettings.points"
            type="number"
            min="0"
            class="form-input"
          />
        </div>
        <div>
          <label class="form-label">Submission Type</label>
          <select v-model="assignmentSettings.submissionType" class="form-input">
            <option value="file">File Upload</option>
            <option value="text">Text Entry</option>
            <option value="url">Website URL</option>
            <option value="media">Media Recording</option>
          </select>
        </div>
        <div class="flex items-center space-x-4">
          <label class="inline-flex items-center">
            <input
              v-model="assignmentSettings.allowLateSubmissions"
              type="checkbox"
              class="form-checkbox text-maroon-600"
            />
            <span class="ml-2 text-sm text-gray-900">Allow Late Submissions</span>
          </label>
          <div v-if="assignmentSettings.allowLateSubmissions">
            <input
              v-model.number="assignmentSettings.latePenalty"
              type="number"
              min="0"
              max="100"
              class="w-16 form-input"
              placeholder="%"
            />
            <span class="text-sm text-gray-600">% penalty per day</span>
          </div>
        </div>
      </div>

      <!-- Group Settings -->
      <div class="mt-4">
        <label class="inline-flex items-center">
          <input
            v-model="assignmentSettings.groupSubmission"
            type="checkbox"
            class="form-checkbox text-maroon-600"
          />
          <span class="ml-2 text-sm text-gray-900">Allow Group Submission</span>
        </label>
        <div v-if="assignmentSettings.groupSubmission" class="mt-2">
          <label class="form-label">Maximum Group Size</label>
          <input
            v-model.number="assignmentSettings.maxGroupSize"
            type="number"
            min="2"
            class="w-24 form-input"
          />
        </div>
      </div>

      <!-- Peer Review Settings -->
      <div class="mt-4">
        <label class="inline-flex items-center">
          <input
            v-model="assignmentSettings.peerReview"
            type="checkbox"
            class="form-checkbox text-maroon-600"
          />
          <span class="ml-2 text-sm text-gray-900">Enable Peer Review</span>
        </label>
        <div v-if="assignmentSettings.peerReview" class="mt-2 grid grid-cols-2 gap-4">
          <div>
            <label class="form-label">Number of Reviewers</label>
            <input
              v-model.number="assignmentSettings.reviewers"
              type="number"
              min="1"
              class="form-input"
            />
          </div>
          <div>
            <label class="form-label">Review Due Date</label>
            <input
              v-model="assignmentSettings.reviewDueDate"
              type="datetime-local"
              class="form-input"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- File Uploader -->
    <FileUploader
      :content-type="'assignment'"
      @file-selected="handleFileSelected"
      @file-removed="handleFileRemoved"
    />

    <!-- Preview Mode -->
    <div v-if="previewMode" class="preview-mode">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Assignment Preview</h3>
        <span class="text-sm text-gray-600">Preview Mode</span>
      </div>
      
      <div class="space-y-4">
        <div class="metadata-field">
          <span class="material-icons">event</span>
          <span>Due: {{ formatDate(assignmentSettings.dueDate) }}</span>
        </div>
        <div class="metadata-field">
          <span class="material-icons">stars</span>
          <span>Points: {{ assignmentSettings.points }}</span>
        </div>
        <div class="p-4 bg-white rounded-lg shadow-sm">
          <h3 class="font-medium text-gray-900 mb-2">Submission</h3>
          <div class="text-gray-800">
            {{ getSubmissionTypeText(assignmentSettings.submissionType) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import FileUploader from './FileUploader.vue'

export default {
  name: 'AssignmentBuilder',
  components: {
    FileUploader
  },
  props: {
    previewMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:assignment'],
  setup(props, { emit }) {
    const toast = useToast()
    
    const assignmentSettings = ref({
      dueDate: null,
      points: 0,
      submissionType: 'file',
      allowLateSubmissions: false,
      latePenalty: 0,
      groupSubmission: false,
      maxGroupSize: 2,
      peerReview: false,
      reviewers: 0,
      reviewDueDate: null
    })

    const selectedFile = ref(null)

    const handleFileSelected = (file) => {
      selectedFile.value = file
    }

    const handleFileRemoved = () => {
      selectedFile.value = null
    }

    const validateAssignment = () => {
      if (!assignmentSettings.value.dueDate) {
        toast.error('Due date is required')
        return false
      }

      if (assignmentSettings.value.points <= 0) {
        toast.error('Points must be greater than 0')
        return false
      }

      if (assignmentSettings.value.peerReview) {
        if (!assignmentSettings.value.reviewers || !assignmentSettings.value.reviewDueDate) {
          toast.error('Peer review settings are incomplete')
          return false
        }
        if (new Date(assignmentSettings.value.reviewDueDate) <= new Date(assignmentSettings.value.dueDate)) {
          toast.error('Review due date must be after assignment due date')
          return false
        }
      }

      return true
    }

    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleString()
    }

    const getSubmissionTypeText = (type) => {
      const types = {
        file: 'File Upload',
        text: 'Text Entry',
        url: 'Website URL',
        media: 'Media Recording'
      }
      return types[type] || type
    }

    watch([assignmentSettings, selectedFile], () => {
      if (validateAssignment()) {
        emit('update:assignment', {
          settings: assignmentSettings.value,
          file: selectedFile.value
        })
      }
    }, { deep: true })

    return {
      assignmentSettings,
      handleFileSelected,
      handleFileRemoved,
      formatDate,
      getSubmissionTypeText
    }
  }
}
</script>

<style scoped>
.form-input {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-maroon-500 focus:border-maroon-500 transition-all duration-200;
}

.form-label {
  @apply block text-sm font-medium text-gray-900 mb-1;
}

.form-checkbox {
  @apply rounded border-gray-300 text-maroon-600 focus:ring-maroon-500;
}

.preview-mode {
  @apply bg-gray-100 p-4 rounded-lg border border-gray-300;
}

.metadata-field {
  @apply flex items-center space-x-2 text-sm text-gray-600;
}
</style> 