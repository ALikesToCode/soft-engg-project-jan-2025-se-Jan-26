<template>
  <div class="space-y-6">
    <!-- Quiz Settings -->
    <div class="form-section">
      <h3 class="text-lg font-medium text-gray-900">Quiz Settings</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="form-label">Time Limit (minutes)</label>
          <input
            v-model.number="quizSettings.timeLimit"
            type="number"
            min="0"
            class="form-input"
          />
        </div>
        <div>
          <label class="form-label">Allowed Attempts</label>
          <input
            v-model.number="quizSettings.allowedAttempts"
            type="number"
            min="1"
            class="form-input"
          />
        </div>
        <div>
          <label class="form-label">Passing Score (%)</label>
          <input
            v-model.number="quizSettings.passingScore"
            type="number"
            min="0"
            max="100"
            class="form-input"
          />
        </div>
        <div>
          <label class="form-label">Points per Question</label>
          <input
            v-model.number="quizSettings.points"
            type="number"
            min="0"
            class="form-input"
          />
        </div>
      </div>
    </div>

    <!-- Questions -->
    <div class="space-y-4">
      <div v-for="(question, index) in questions" :key="index" class="p-4 bg-gray-50 rounded-lg">
        <div class="flex justify-between items-start mb-2">
          <h3 class="font-medium">Question {{ index + 1 }}</h3>
          <button @click="removeQuestion(index)" class="text-red-600 hover:text-red-700">
            <span class="material-icons">delete</span>
          </button>
        </div>
        <input
          v-model="question.text"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-2"
          placeholder="Enter question"
        />
        <div class="space-y-2">
          <div v-for="(option, optIndex) in question.options" :key="optIndex" class="flex items-center space-x-2">
            <input
              :id="'q'+index+'opt'+optIndex"
              type="radio"
              :name="'question'+index"
              :value="optIndex"
              v-model="question.correctAnswer"
              class="text-maroon-600"
            />
            <input
              v-model="question.options[optIndex]"
              type="text"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
              :placeholder="'Option ' + (optIndex + 1)"
            />
          </div>
        </div>
      </div>
      <button
        @click="addQuestion"
        class="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-maroon-500 hover:text-maroon-600"
      >
        <span class="material-icons">add</span> Add Question
      </button>
    </div>

    <!-- Preview Mode -->
    <div v-if="previewMode" class="preview-mode">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">Quiz Preview</h3>
        <span class="text-sm text-gray-600">Preview Mode</span>
      </div>
      
      <div class="space-y-6">
        <div v-for="(question, index) in questions" :key="index" class="p-4 bg-white rounded-lg shadow-sm">
          <p class="font-medium text-gray-900 mb-3">{{ index + 1 }}. {{ question.text }}</p>
          <div class="space-y-2">
            <label
              v-for="(option, optIndex) in question.options"
              :key="optIndex"
              class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50"
            >
              <input
                type="radio"
                :name="'preview-q'+index"
                :value="optIndex"
                disabled
                class="text-maroon-600"
              />
              <span class="text-gray-800">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'QuizBuilder',
  props: {
    previewMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:quiz'],
  setup(props, { emit }) {
    const toast = useToast()
    
    const questions = ref([])
    const quizSettings = ref({
      timeLimit: 60,
      allowedAttempts: 1,
      passingScore: 70,
      points: 1
    })

    const addQuestion = () => {
      questions.value.push({
        text: '',
        type: 'multiple-choice',
        options: ['', '', '', ''],
        correctAnswer: null,
        points: quizSettings.value.points,
        explanation: '',
        feedback: {
          correct: '',
          incorrect: ''
        }
      })
    }

    const removeQuestion = (index) => {
      questions.value.splice(index, 1)
    }

    const validateQuiz = () => {
      if (questions.value.length === 0) {
        toast.error('Quiz must have at least one question')
        return false
      }

      for (const question of questions.value) {
        if (!question.text.trim()) {
          toast.error('All questions must have text')
          return false
        }
        if (question.correctAnswer === null) {
          toast.error('All questions must have a correct answer selected')
          return false
        }
        if (question.options.some(opt => !opt.trim())) {
          toast.error('All options must be filled out')
          return false
        }
      }

      return true
    }

    watch([questions, quizSettings], () => {
      if (validateQuiz()) {
        emit('update:quiz', {
          questions: questions.value,
          settings: quizSettings.value
        })
      }
    }, { deep: true })

    return {
      questions,
      quizSettings,
      addQuestion,
      removeQuestion
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

.preview-mode {
  @apply bg-gray-100 p-4 rounded-lg border border-gray-300;
}
</style> 