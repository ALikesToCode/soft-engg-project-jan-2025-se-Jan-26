import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { getCourseById, getLectureById } from '../mock-data/courses'
import { useNotification } from './useNotification'
import { useCourseState } from './useCourseState'

const STORAGE_KEY = 'course_progress'

export function useCourse(courseId) {
  const { notify } = useNotification()
  const { saveNote, getNote } = useCourseState()
  const currentCourse = ref(null)
  const selectedLecture = ref(null)
  const isBookmarked = ref(false)
  const showNotes = ref(false)
  const currentNotes = ref('')
  const loading = ref(true)
  const error = ref(null)

  // Load course data with error handling
  const loadCourse = async () => {
    try {
      loading.value = true
      error.value = null

      // In production, this would be an API call
      const course = await getCourseById(courseId)
      if (!course) {
        throw new Error('Course not found')
      }
      currentCourse.value = course
      isBookmarked.value = course.isBookmarked || false

      // Load saved progress
      loadProgress()
    } catch (err) {
      error.value = err.message
      // notify.error('Failed to load course data')
    } finally {
      loading.value = false
    }
  }

  // Save progress to localStorage
  const saveProgress = () => {
    if (!currentCourse.value) return

    const progress = {
      courseId: currentCourse.value.id,
      completedLectures: completedLectures.value,
      lastLectureId: selectedLecture.value?.id,
      notes: currentNotes.value,
      timestamp: Date.now()
    }

    try {
      localStorage.setItem(
        `${STORAGE_KEY}_${courseId}`,
        JSON.stringify(progress)
      )
    } catch (err) {
      console.error('Failed to save progress:', err)
    }
  }

  // Load progress from localStorage
  const loadProgress = () => {
    try {
      const saved = localStorage.getItem(`${STORAGE_KEY}_${courseId}`)
      if (saved) {
        const progress = JSON.parse(saved)

        // Restore completed lectures
        if (progress.completedLectures) {
          currentCourse.value.syllabus.forEach(week => {
            week.lectures.forEach(lecture => {
              lecture.completed = progress.completedLectures.includes(lecture.id)
            })
          })
        }

        // Restore last viewed lecture
        if (progress.lastLectureId) {
          const lastLecture = findLectureById(progress.lastLectureId)
          if (lastLecture) {
            selectedLecture.value = lastLecture
          }
        }

        // Restore notes
        if (progress.notes) {
          currentNotes.value = progress.notes
        }
      }
    } catch (err) {
      console.error('Failed to load progress:', err)
    }
  }

  const findLectureById = (lectureId) => {
    for (const week of weeks.value) {
      const lecture = week.lectures.find(l => l.id === lectureId)
      if (lecture) return lecture
    }
    return null
  }

  const completedLectures = computed(() => {
    if (!currentCourse.value) return []
    const completed = []
    currentCourse.value.syllabus.forEach(week => {
      week.lectures.forEach(lecture => {
        if (lecture.completed) {
          completed.push(lecture.id)
        }
      })
    })
    return completed
  })

  const completedLecturesCount = computed(() => {
    return completedLectures.value.length
  })

  const totalLectures = computed(() => {
    if (!currentCourse.value) return 0
    return currentCourse.value.syllabus.reduce((acc, week) =>
      acc + week.lectures.length, 0)
  })

  const weeks = computed(() => currentCourse.value?.syllabus || [])

  const selectLecture = (lecture) => {
    selectedLecture.value = lecture
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const toggleBookmark = async () => {
    if (!currentCourse.value) return
    isBookmarked.value = !isBookmarked.value
    try {
      // await api.updateBookmark(currentCourse.value.id, isBookmarked.value)
    } catch (error) {
      console.error('Bookmark update failed:', error)
      isBookmarked.value = !isBookmarked.value
    }
  }

  const toggleNotes = () => {
    showNotes.value = !showNotes.value
  }

  const markAsComplete = () => {
    if (selectedLecture.value) {
      selectedLecture.value.completed = !selectedLecture.value.completed
      // Update the lecture in the course syllabus
      const week = weeks.value.find(week =>
        week.lectures.some(lecture => lecture.id === selectedLecture.value.id)
      )
      if (week) {
        const lecture = week.lectures.find(lecture => lecture.id === selectedLecture.value.id)
        if (lecture) {
          lecture.completed = selectedLecture.value.completed
        }
      }
    }
  }

  const getWeekProgress = (week) => {
    const completedInWeek = week.lectures.filter(lecture => lecture.completed).length
    return Math.round((completedInWeek / week.lectures.length) * 100) || 0
  }

  const getFileIcon = (type) => {
    const icons = {
      'pdf': 'fa-file-pdf',
      'ppt': 'fa-file-powerpoint',
      'doc': 'fa-file-word',
      'txt': 'fa-file-alt',
      'default': 'fa-file'
    }
    return icons[type] || icons.default
  }

  const saveNotes = async (lectureId, notes) => {
    if (!lectureId) return
    try {
      saveNote(courseId, lectureId, notes)
      return true
    } catch (err) {
      console.error('Failed to save notes:', err)
      throw err
    }
  }

  const fetchNotes = async (lectureId) => {
    if (!lectureId) return ''
    try {
      return getNote(courseId, lectureId)
    } catch (err) {
      console.error('Failed to fetch notes:', err)
      throw err
    }
  }

  // Initialize with first lecture if none selected
  if (currentCourse.value && !selectedLecture.value && weeks.value.length > 0) {
    const firstWeek = weeks.value[0]
    if (firstWeek.lectures.length > 0) {
      selectLecture(firstWeek.lectures[0])
    }
  }

  // Add auto-save on component unmount
  onBeforeUnmount(() => {
    saveProgress()
  })

  // Initialize
  onMounted(() => {
    loadCourse()
  })

  return {
    currentCourse,
    selectedLecture,
    isBookmarked,
    showNotes,
    currentNotes,
    completedLectures,
    completedLecturesCount,
    totalLectures,
    weeks,
    loading,
    error,
    selectLecture,
    toggleBookmark,
    toggleNotes,
    markAsComplete,
    getWeekProgress,
    getFileIcon,
    saveProgress,
    loadProgress,
    saveNotes,
    fetchNotes
  }
} 