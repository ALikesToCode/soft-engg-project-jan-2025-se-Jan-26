import axios from 'axios';

// Mock data for development
const mockFaqs = [
  {
    id: 1,
    question: 'How do I reset my password?',
    answer: 'To reset your password:<br>1. Click on "Forgot Password" on the login page<br>2. Enter your email address<br>3. Check your email for reset instructions<br>4. Follow the link and create a new password',
    categoryId: 'account',
    priority: 5
  },
  {
    id: 2,
    question: 'How do I enroll in a course?',
    answer: 'To enroll in a course:<br>1. Go to the Courses page<br>2. Find the course you want to join<br>3. Click the "Enroll" button<br>4. Confirm your enrollment',
    categoryId: 'courses',
    priority: 4
  },
  {
    id: 3,
    question: 'What should I do if I encounter technical issues during a quiz?',
    answer: 'If you experience technical issues during a quiz:<br>1. Take a screenshot of the error<br>2. Contact support immediately<br>3. Do not close your browser<br>4. Wait for support staff assistance',
    categoryId: 'technical',
    priority: 4
  },
  {
    id: 4,
    question: 'How can I track my course progress?',
    answer: 'You can track your course progress by:<br>1. Going to your Dashboard<br>2. Checking the progress bars for each course<br>3. Viewing detailed analytics in the Course History section',
    categoryId: 'general',
    priority: 3
  },
  {
    id: 5,
    question: 'What file formats are supported for assignment submissions?',
    answer: 'The following file formats are supported:<br>- PDF (.pdf)<br>- Word documents (.doc, .docx)<br>- Text files (.txt)<br>- Images (.jpg, .png)<br>- ZIP archives (.zip) for multiple files',
    categoryId: 'technical',
    priority: 3
  },
  {
    id: 6,
    question: 'How do I contact my course instructor?',
    answer: 'To contact your instructor:<br>1. Go to the course page<br>2. Click on the "Contact Instructor" button<br>3. Fill out the contact form<br>4. Your message will be sent directly to the instructor',
    categoryId: 'courses',
    priority: 2
  },
  {
    id: 7,
    question: 'What are the system requirements for video lectures?',
    answer: 'Recommended system requirements:<br>- Modern web browser (Chrome, Firefox, Safari)<br>- Stable internet connection (minimum 5 Mbps)<br>- Updated video codecs<br>- Enabled JavaScript',
    categoryId: 'technical',
    priority: 2
  },
  {
    id: 8,
    question: 'How do I get a certificate after completing a course?',
    answer: 'To receive your certificate:<br>1. Complete all required course modules<br>2. Pass the final assessment<br>3. Go to the Course Completion page<br>4. Click "Generate Certificate"<br>5. Download or share your certificate',
    categoryId: 'courses',
    priority: 3
  }
]

// Force development mode for now until backend is ready
const isDevelopment = true

class FAQService {
  async getAllFaqs() {
    // Always return mock data for now
    return Promise.resolve(mockFaqs)
  }

  async getFaqsByCategory(category) {
    // Filter mock data by category
    const filteredFaqs = category === 'all' 
      ? mockFaqs 
      : mockFaqs.filter(faq => faq.categoryId === category)
    return Promise.resolve(filteredFaqs)
  }

  async createFaq(faqData) {
    const newFaq = {
      id: mockFaqs.length + 1,
      ...faqData
    }
    mockFaqs.push(newFaq)
    return Promise.resolve({ data: newFaq })
  }

  async updateFaq(faqId, faqData) {
    const index = mockFaqs.findIndex(f => f.id === faqId)
    if (index !== -1) {
      mockFaqs[index] = { ...mockFaqs[index], ...faqData }
      return Promise.resolve({ data: mockFaqs[index] })
    }
    throw new Error('FAQ not found')
  }

  async deleteFaq(faqId) {
    const index = mockFaqs.findIndex(f => f.id === faqId)
    if (index !== -1) {
      mockFaqs.splice(index, 1)
      return Promise.resolve()
    }
    throw new Error('FAQ not found')
  }

  async rateFaq(faqId, isHelpful) {
    const faq = mockFaqs.find(f => f.id === faqId)
    if (faq) {
      faq.ratings = faq.ratings || { helpful: 0, unhelpful: 0 }
      if (isHelpful) {
        faq.ratings.helpful++
      } else {
        faq.ratings.unhelpful++
      }
      return Promise.resolve({ data: { ratings: faq.ratings } })
    }
    throw new Error('FAQ not found')
  }

  async searchFaqs(query) {
    const lowercaseQuery = query.toLowerCase()
    const results = mockFaqs.filter(
      faq =>
        faq.question.toLowerCase().includes(lowercaseQuery) ||
        faq.answer.toLowerCase().includes(lowercaseQuery)
    )
    return Promise.resolve(results)
  }

  async submitSupportRequest(requestData) {
    console.log('Support request submitted:', requestData)
    return Promise.resolve({ success: true })
  }
}

export default new FAQService() 