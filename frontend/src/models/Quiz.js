export class Quiz {
  constructor(data = {}) {
    this.id = data.id || null
    this.title = data.title || ''
    this.description = data.description || ''
    this.moduleId = data.moduleId || null
    this.courseId = data.courseId || null
    this.questions = data.questions || []
    this.status = data.status || 'draft'
    this.metadata = {
      timeLimit: data.metadata?.timeLimit || null,
      passingScore: data.metadata?.passingScore || 70,
      allowedAttempts: data.metadata?.allowedAttempts || 1,
      points: data.metadata?.points || 0,
      gradingType: data.metadata?.gradingType || 'auto',
      visibility: data.metadata?.visibility || 'hidden'
    }
  }

  isValid() {
    return (
      this.title.trim() !== '' &&
      this.description.trim() !== '' &&
      this.moduleId !== null &&
      this.courseId !== null &&
      this.questions.length > 0 &&
      this.questions.every(q => this.isValidQuestion(q))
    )
  }

  isValidQuestion(question) {
    return (
      question.text?.trim() !== '' &&
      Array.isArray(question.options) &&
      question.options.length >= 2 &&
      question.options.every(opt => opt.trim() !== '') &&
      question.correctAnswer !== null &&
      question.correctAnswer >= 0 &&
      question.correctAnswer < question.options.length
    )
  }

  toJSON() {
    return {
      id: this.id,
      title: this.title,
      description: this.description,
      moduleId: this.moduleId,
      courseId: this.courseId,
      questions: this.questions,
      status: this.status,
      metadata: this.metadata
    }
  }
} 