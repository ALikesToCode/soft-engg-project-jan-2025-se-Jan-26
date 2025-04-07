<template>
  <div class="transcription-container">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p class="loading-text">{{ loadingText }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">
        <span class="material-symbols-outlined text-red-500 text-3xl">error_outline</span>
      </div>
      <p class="error-message">{{ error }}</p>
      <button 
        v-if="!transcriptionExists" 
        @click="generateTranscript" 
        class="generate-btn"
        :disabled="generatingTranscript"
      >
        <span class="material-symbols-outlined">description</span>
        {{ generatingTranscript ? 'Generating...' : 'Generate Transcript' }}
      </button>
    </div>

    <div v-else class="transcription-content">
      <!-- Tabs for Transcript and Summary -->
      <div class="tab-bar">
        <button 
          @click="activeTab = 'transcript'" 
          :class="{ 'active': activeTab === 'transcript' }"
          class="tab-btn"
        >
          <span class="material-symbols-outlined">description</span>
          Transcript
        </button>
        <button 
          @click="activeTab = 'summary'" 
          :class="{ 'active': activeTab === 'summary' }"
          class="tab-btn"
          :disabled="!transcription.ai_summary"
        >
          <span class="material-symbols-outlined">summarize</span>
          AI Summary
        </button>
      </div>

      <!-- Transcript Content -->
      <div v-if="activeTab === 'transcript'" class="transcript-text">
        <div class="controls">
          <div class="search-bar">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search in transcript..." 
              class="search-input"
            />
            <button @click="search" class="search-btn">
              <span class="material-symbols-outlined">search</span>
            </button>
          </div>
          <button @click="copyTranscript" class="action-btn">
            <span class="material-symbols-outlined">content_copy</span>
          </button>
        </div>

        <div v-if="searchResults.length > 0" class="search-results">
          <p class="results-count">{{ searchResults.length }} matches found</p>
          <div v-for="(result, index) in searchResults" :key="index" class="result-item">
            <p v-html="highlightMatch(result)"></p>
          </div>
        </div>

        <div v-else class="transcript-content">
          <p v-html="processedTranscript"></p>
        </div>
      </div>

      <!-- AI Summary Content -->
      <div v-else-if="activeTab === 'summary'" class="summary-content">
        <div v-if="!transcription.ai_summary" class="no-summary">
          <p>No AI summary available yet.</p>
          <button @click="generateSummary" class="generate-btn" :disabled="generatingSummary">
            <span class="material-symbols-outlined">auto_awesome</span>
            {{ generatingSummary ? 'Generating...' : 'Generate Summary' }}
          </button>
        </div>
        <div v-else class="summary-text">
          <div class="controls">
            <button @click="copySummary" class="action-btn">
              <span class="material-symbols-outlined">content_copy</span>
            </button>
          </div>
          <div v-html="formattedSummary"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import api from '@/utils/api';

export default {
  name: 'LectureTranscription',
  props: {
    lectureId: {
      type: [Number, String],
      required: true
    }
  },
  setup(props) {
    const loading = ref(true);
    const error = ref(null);
    const transcription = ref(null);
    const activeTab = ref('transcript');
    const searchQuery = ref('');
    const searchResults = ref([]);
    const generatingTranscript = ref(false);
    const generatingSummary = ref(false);
    const transcriptionExists = ref(false);
    const loadingText = ref('Loading transcription...');

    // Process the transcript for better readability
    const processedTranscript = computed(() => {
      if (!transcription.value?.transcription_text) return '';
      
      // Add paragraph breaks after sentences for better readability
      const text = transcription.value.transcription_text
        .replace(/\.\s+/g, '.<br><br>') // Add breaks after periods
        .replace(/\?\s+/g, '?<br><br>') // Add breaks after question marks
        .replace(/!\s+/g, '!<br><br>'); // Add breaks after exclamation marks
      
      return text;
    });

    // Format the AI summary with Markdown
    const formattedSummary = computed(() => {
      if (!transcription.value?.ai_summary) return '';
      
      try {
        // Use marked to render markdown
        const html = marked(transcription.value.ai_summary);
        
        // Sanitize the HTML
        return DOMPurify.sanitize(html);
      } catch (error) {
        console.error('Error formatting summary:', error);
        return transcription.value.ai_summary;
      }
    });

    // Load the transcription data
    const loadTranscription = async () => {
      try {
        loading.value = true;
        loadingText.value = 'Loading transcription...';
        const token = localStorage.getItem('token');
        
        if (!token) {
          error.value = 'Authentication required';
          return;
        }
        
        const response = await api.get(`/api/v1/transcription/${props.lectureId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        transcription.value = response.data;
        transcriptionExists.value = true;
        error.value = null;
      } catch (err) {
        if (err.response && err.response.status === 404) {
          transcriptionExists.value = false;
          error.value = 'No transcription available for this lecture.';
        } else {
          error.value = err.response?.data?.detail || 'Failed to load transcription';
        }
        transcription.value = null;
      } finally {
        loading.value = false;
      }
    };

    // Generate transcript from video
    const generateTranscript = async () => {
      try {
        generatingTranscript.value = true;
        error.value = null;
        loadingText.value = 'Extracting transcript from video...';
        loading.value = true;
        
        const token = localStorage.getItem('token');
        if (!token) {
          error.value = 'Authentication required';
          return;
        }
        
        const response = await api.post(`/api/v1/transcription/extract/${props.lectureId}`, null, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        transcription.value = response.data;
        transcriptionExists.value = true;
        error.value = null;
        activeTab.value = 'transcript';
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to generate transcription';
      } finally {
        generatingTranscript.value = false;
        loading.value = false;
      }
    };

    // Generate AI summary
    const generateSummary = async () => {
      try {
        generatingSummary.value = true;
        
        const token = localStorage.getItem('token');
        if (!token) {
          error.value = 'Authentication required';
          return;
        }
        
        const response = await api.post('/api/v1/transcription/summary', {
          lecture_id: parseInt(props.lectureId),
          max_length: 500
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // Update the transcription with the new summary
        transcription.value = {
          ...transcription.value,
          ai_summary: response.data.summary
        };
      } catch (err) {
        console.error('Error generating summary:', err);
        // Show error message but don't change the tab
      } finally {
        generatingSummary.value = false;
      }
    };

    // Search in transcript
    const search = () => {
      if (!searchQuery.value || !transcription.value?.transcription_text) {
        searchResults.value = [];
        return;
      }
      
      const query = searchQuery.value.toLowerCase();
      const text = transcription.value.transcription_text.toLowerCase();
      
      // Simple way to split text into blocks for search results
      const sentences = transcription.value.transcription_text.split(/[.!?]+\s+/);
      
      // Find sentences containing the search query
      searchResults.value = sentences.filter(sentence => 
        sentence.toLowerCase().includes(query)
      );
    };

    // Highlight search matches
    const highlightMatch = (text) => {
      if (!searchQuery.value) return text;
      
      const query = searchQuery.value;
      const regex = new RegExp(`(${query})`, 'gi');
      return text.replace(regex, '<mark>$1</mark>');
    };

    // Copy transcript to clipboard
    const copyTranscript = () => {
      if (!transcription.value?.transcription_text) return;
      
      navigator.clipboard.writeText(transcription.value.transcription_text)
        .then(() => {
          alert('Transcript copied to clipboard');
        })
        .catch(err => {
          console.error('Failed to copy:', err);
        });
    };

    // Copy summary to clipboard
    const copySummary = () => {
      if (!transcription.value?.ai_summary) return;
      
      navigator.clipboard.writeText(transcription.value.ai_summary)
        .catch(err => {
          console.error('Failed to copy:', err);
        });
    };

    // Watch for changes in lectureId
    watch(() => props.lectureId, (newId) => {
      if (newId) {
        loadTranscription();
      }
    });

    // Initialize on mount
    onMounted(() => {
      if (props.lectureId) {
        loadTranscription();
      }
    });

    // Clear search results when query is empty
    watch(searchQuery, (newQuery) => {
      if (!newQuery) {
        searchResults.value = [];
      }
    });

    return {
      loading,
      error,
      transcription,
      activeTab,
      searchQuery,
      searchResults,
      processedTranscript,
      formattedSummary,
      generatingTranscript,
      generatingSummary,
      transcriptionExists,
      loadingText,
      
      loadTranscription,
      generateTranscript,
      generateSummary,
      search,
      highlightMatch,
      copyTranscript,
      copySummary
    };
  }
};
</script>

<style scoped>
.transcription-container {
  @apply bg-white rounded-lg shadow-md p-4 h-full flex flex-col overflow-hidden;
}

.loading-state {
  @apply flex flex-col items-center justify-center h-full;
}

.spinner {
  @apply w-10 h-10 border-4 border-maroon-500 border-t-transparent rounded-full animate-spin;
}

.loading-text {
  @apply mt-4 text-slate-600;
}

.error-state {
  @apply flex flex-col items-center justify-center h-full text-center p-8;
}

.error-icon {
  @apply mb-4;
}

.error-message {
  @apply text-slate-700 mb-6;
}

.generate-btn {
  @apply flex items-center gap-2 bg-maroon-600 text-white px-4 py-2 rounded-lg hover:bg-maroon-700 transition-colors;
}

.generate-btn:disabled {
  @apply bg-slate-400 cursor-not-allowed;
}

.tab-bar {
  @apply flex border-b border-slate-200 mb-4;
}

.tab-btn {
  @apply flex items-center gap-2 px-4 py-2 text-slate-600 border-b-2 border-transparent;
}

.tab-btn.active {
  @apply text-maroon-600 border-maroon-600;
}

.tab-btn:disabled {
  @apply text-slate-400 cursor-not-allowed;
}

.controls {
  @apply flex justify-between mb-4;
}

.search-bar {
  @apply flex;
}

.search-input {
  @apply border border-slate-300 rounded-l-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-maroon-500;
}

.search-btn {
  @apply bg-maroon-600 text-white px-2 rounded-r-lg hover:bg-maroon-700 transition-colors;
}

.action-btn {
  @apply text-slate-600 hover:text-maroon-600 transition-colors;
}

.transcript-text, .summary-content {
  @apply flex-1 overflow-auto;
}

.transcript-content, .summary-text {
  @apply p-2;
}

.search-results {
  @apply border border-slate-200 rounded-lg p-4 mb-4;
}

.results-count {
  @apply text-sm text-slate-500 mb-2;
}

.result-item {
  @apply border-b border-slate-100 py-2 last:border-0;
}

.result-item mark {
  @apply bg-yellow-200 px-0.5 rounded;
}

.no-summary {
  @apply flex flex-col items-center justify-center p-8;
}
</style> 