<template>
  <div class="lecture-notes h-full flex flex-col">
    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
      <h3 class="text-lg font-semibold">Your Notes</h3>
      <div class="flex space-x-2">
        <button 
          @click="saveNotes" 
          class="p-2 text-sm bg-primary text-white rounded hover:bg-primary-dark transition-colors"
          :disabled="isSaving"
        >
          <span v-if="isSaving">Saving...</span>
          <span v-else>Save</span>
        </button>
      </div>
    </div>
    
    <div class="flex-1 overflow-y-auto">
      <!-- Empty state -->
      <div v-if="!notes.length && !currentNote" class="flex flex-col items-center justify-center h-full p-6 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        <p class="text-gray-600 dark:text-gray-400 mb-4">No notes yet. Start taking notes for this lecture.</p>
        <button 
          @click="createNewNote" 
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
        >
          Create Note
        </button>
      </div>
      
      <!-- List of existing notes -->
      <div v-else-if="notes.length && !currentNote" class="p-4 space-y-3">
        <div 
          v-for="note in notes" 
          :key="note.id" 
          @click="editNote(note)"
          class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-medium text-sm">{{ formatTime(note.timestamp) }}</h4>
            <div class="flex space-x-2">
              <button 
                @click.stop="deleteNote(note.id)" 
                class="text-red-500 hover:text-red-700 transition-colors"
                title="Delete note"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
          <p class="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">{{ note.content }}</p>
        </div>
        
        <button 
          @click="createNewNote" 
          class="w-full p-3 bg-gray-100 dark:bg-gray-700 rounded-lg text-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          + New Note
        </button>
      </div>
      
      <!-- Note editor -->
      <div v-else-if="currentNote" class="p-4 h-full flex flex-col">
        <div class="mb-3 flex justify-between items-center">
          <span class="text-sm text-gray-600 dark:text-gray-400">
            {{ formatTime(currentNote.timestamp || Date.now()) }}
          </span>
          <button 
            @click="closeEditor" 
            class="text-gray-600 hover:text-gray-800 transition-colors"
            title="Close editor"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <textarea
          v-model="currentNote.content"
          class="flex-1 w-full p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
          placeholder="Type your notes here..."
          @keydown.ctrl.enter="saveAndCloseEditor"
        ></textarea>
        
        <div class="mt-3 flex justify-end space-x-3">
          <button 
            @click="closeEditor" 
            class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="saveAndCloseEditor" 
            class="px-3 py-1.5 bg-primary text-white rounded hover:bg-primary-dark transition-colors"
            :disabled="isSaving"
          >
            <span v-if="isSaving">Saving...</span>
            <span v-else>Save Note</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  props: {
    lectureId: {
      type: String,
      required: true
    },
    courseId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const notes = ref([]);
    const currentNote = ref(null);
    const isSaving = ref(false);
    
    // Fetch notes from localStorage or API
    const fetchNotes = () => {
      const storageKey = `notes_${props.courseId}_${props.lectureId}`;
      const savedNotes = localStorage.getItem(storageKey);
      
      if (savedNotes) {
        notes.value = JSON.parse(savedNotes);
      }
    };
    
    // Save notes to localStorage or API
    const saveNotes = async () => {
      if (currentNote.value) {
        // Save current note
        const noteToSave = { ...currentNote.value };
        
        if (!noteToSave.id) {
          // New note
          noteToSave.id = Date.now().toString();
          noteToSave.timestamp = Date.now();
          notes.value.push(noteToSave);
        } else {
          // Update existing note
          const noteIndex = notes.value.findIndex(n => n.id === noteToSave.id);
          if (noteIndex !== -1) {
            notes.value[noteIndex] = noteToSave;
          }
        }
      }
      
      // Save to localStorage
      const storageKey = `notes_${props.courseId}_${props.lectureId}`;
      localStorage.setItem(storageKey, JSON.stringify(notes.value));
      
      // Here you could also save to an API
      // await saveNotesToApi();
    };
    
    // Create a new note
    const createNewNote = () => {
      currentNote.value = {
        id: '',
        content: '',
        timestamp: Date.now(),
        lectureId: props.lectureId,
        courseId: props.courseId
      };
    };
    
    // Edit an existing note
    const editNote = (note) => {
      currentNote.value = { ...note };
    };
    
    // Delete a note
    const deleteNote = (noteId) => {
      if (confirm('Are you sure you want to delete this note?')) {
        notes.value = notes.value.filter(n => n.id !== noteId);
        saveNotes();
      }
    };
    
    // Close the editor
    const closeEditor = () => {
      currentNote.value = null;
    };
    
    // Save and close the editor
    const saveAndCloseEditor = async () => {
      isSaving.value = true;
      await saveNotes();
      isSaving.value = false;
      closeEditor();
    };
    
    // Format timestamp to readable time
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    onMounted(() => {
      fetchNotes();
    });
    
    return {
      notes,
      currentNote,
      isSaving,
      saveNotes,
      createNewNote,
      editNote,
      deleteNote,
      closeEditor,
      saveAndCloseEditor,
      formatTime
    };
  }
};
</script>

<style scoped>
.lecture-notes {
  @apply bg-white dark:bg-gray-900;
}
</style> 