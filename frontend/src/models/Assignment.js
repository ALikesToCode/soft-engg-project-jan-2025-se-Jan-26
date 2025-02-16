export class Assignment {
  constructor(data = {}) {
    this.id = data.id || null
    this.title = data.title || ''
    this.description = data.description || ''
    this.moduleId = data.moduleId || null
    this.courseId = data.courseId || null
    this.status = data.status || 'draft'
    this.metadata = {
      dueDate: data.metadata?.dueDate || null,
      points: data.metadata?.points || 0,
      gradingType: data.metadata?.gradingType || 'manual',
      visibility: data.metadata?.visibility || 'hidden'
    }
    this.settings = {
      submissionType: data.settings?.submissionType || 'file',
      allowLateSubmissions: data.settings?.allowLateSubmissions || false,
      latePenalty: data.settings?.latePenalty || 0,
      groupSubmission: data.settings?.groupSubmission || false,
      maxGroupSize: data.settings?.maxGroupSize || 1,
      peerReview: data.settings?.peerReview || false,
      reviewers: data.settings?.reviewers || 0,
      reviewDueDate: data.settings?.reviewDueDate || null
    }
  }

  isValid() {
    return (
      this.title.trim() !== '' &&
      this.description.trim() !== '' &&
      this.moduleId !== null &&
      this.courseId !== null &&
      this.metadata.dueDate !== null &&
      this.metadata.points > 0 &&
      this.isValidSettings()
    )
  }

  isValidSettings() {
    if (this.settings.allowLateSubmissions && this.settings.latePenalty < 0) {
      return false
    }

    if (this.settings.groupSubmission && this.settings.maxGroupSize < 2) {
      return false
    }

    if (this.settings.peerReview) {
      return (
        this.settings.reviewers > 0 &&
        this.settings.reviewDueDate !== null &&
        new Date(this.settings.reviewDueDate) > new Date(this.metadata.dueDate)
      )
    }

    return true
  }

  toJSON() {
    return {
      id: this.id,
      title: this.title,
      description: this.description,
      moduleId: this.moduleId,
      courseId: this.courseId,
      status: this.status,
      metadata: this.metadata,
      settings: this.settings
    }
  }
} 