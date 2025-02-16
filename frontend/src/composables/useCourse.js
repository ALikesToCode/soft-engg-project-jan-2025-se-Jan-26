import { ref, computed } from 'vue'
import { getCourseById, getLectureById } from '../mock-data/courses'

export function useCourse(courseId) {
  const currentCourse = ref(getCourseById(parseInt(courseId)))
  const selectedLecture = ref(null)
  const isBookmarked = ref(currentCourse.value?.isBookmarked || false)
  const showNotes = ref(false)
  const currentNotes = ref('')

  const completedLectures = computed(() => {
    if (!currentCourse.value) return 0
    return currentCourse.value.syllabus.reduce((acc, week) => 
      acc + week.lectures.filter(lecture => lecture.completed).length, 0)
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

  // Initialize with first lecture if none selected
  if (currentCourse.value && !selectedLecture.value && weeks.value.length > 0) {
    const firstWeek = weeks.value[0]
    if (firstWeek.lectures.length > 0) {
      selectLecture(firstWeek.lectures[0])
    }
  }

  return {
    currentCourse,
    selectedLecture,
    isBookmarked,
    showNotes,
    currentNotes,
    completedLectures,
    totalLectures,
    weeks,
    selectLecture,
    toggleBookmark,
    toggleNotes,
    markAsComplete,
    getWeekProgress,
    getFileIcon
  }
} 