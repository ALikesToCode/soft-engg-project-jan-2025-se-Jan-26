<template>
  <div class="lecture-content">
    <h1 class="text-2xl font-bold mb-4">{{ lecture.title }}</h1>
    
    <!-- Additional info -->
    <div class="flex items-center mb-6 text-sm text-gray-600 dark:text-gray-400">
      <span v-if="lecture.duration" class="flex items-center mr-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ formatDuration(lecture.duration) }}
      </span>
      <span v-if="lecture.created_at" class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        {{ formatDate(lecture.created_at) }}
      </span>
    </div>
    
    <!-- Lecture description/content -->
    <div v-if="lecture.content" class="prose prose-lg max-w-none dark:prose-invert mb-8">
      <div v-html="renderedContent"></div>
    </div>
    <div v-else class="text-gray-500 italic mb-8">
      No additional content available for this lecture.
    </div>
    
    <!-- Resources and attachments -->
    <div v-if="lecture.resources && lecture.resources.length > 0" class="mt-8">
      <h2 class="text-xl font-semibold mb-4">Additional Resources</h2>
      <ul class="space-y-2">
        <li v-for="(resource, index) in lecture.resources" :key="index" class="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div class="mr-3 text-blue-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1">
            <a 
              :href="resource.url" 
              target="_blank" 
              rel="noopener noreferrer"
              class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              {{ resource.title || resource.url }}
            </a>
            <p v-if="resource.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ resource.description }}
            </p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

export default {
  props: {
    lecture: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    // Render markdown content safely
    const renderedContent = computed(() => {
      if (!props.lecture.content) return '';
      
      // Convert markdown to HTML and sanitize to prevent XSS
      const html = marked(props.lecture.content);
      return DOMPurify.sanitize(html);
    });
    
    // Format duration (e.g., "10:30")
    const formatDuration = (seconds) => {
      if (!seconds) return '';
      
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    };
    
    // Format date (e.g., "Jan 15, 2024")
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    };
    
    return {
      renderedContent,
      formatDuration,
      formatDate
    };
  }
};
</script>

<style>
.lecture-content {
  @apply px-1;
}

/* Style markdown content */
.lecture-content .prose h1 {
  @apply text-2xl font-bold mt-6 mb-4;
}

.lecture-content .prose h2 {
  @apply text-xl font-semibold mt-5 mb-3;
}

.lecture-content .prose h3 {
  @apply text-lg font-medium mt-4 mb-2;
}

.lecture-content .prose p {
  @apply mb-4 leading-relaxed;
}

.lecture-content .prose pre {
  @apply bg-gray-50 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto;
}

.lecture-content .prose code {
  @apply font-mono text-sm bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded;
}

.lecture-content .prose pre code {
  @apply bg-transparent dark:bg-transparent px-0 py-0;
}

.lecture-content .prose blockquote {
  @apply border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic;
}

.lecture-content .prose a {
  @apply text-blue-600 dark:text-blue-400 hover:underline;
}

.lecture-content .prose img {
  @apply rounded-lg max-w-full h-auto my-4;
}

.lecture-content .prose ul {
  @apply list-disc pl-6 mb-4;
}

.lecture-content .prose ol {
  @apply list-decimal pl-6 mb-4;
}
</style>