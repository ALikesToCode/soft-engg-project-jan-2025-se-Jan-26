// Mock data generator for analytics
const generateMockData = (filters) => {
  // Course enrollment data
  const courseEnrollmentData = {
    labels: ['Math', 'CT', 'SE', 'ST'],
    datasets: [{
      label: 'Number of Students',
      data: [95, 90, 78, 110],
      backgroundColor: '#DC2626', // Stronger red for better visibility
      borderRadius: 6,
    }]
  }

  // Grade distribution data for different courses
  const gradeDistributionData = {
    labels: ['S', 'A', 'B', 'C', 'D', 'Fail'],
    datasets: [{
      data: [25, 35, 25, 8, 4, 3],
      backgroundColor: [
        '#2563EB', // S - Stronger Blue
        '#059669', // A - Stronger Green
        '#D97706', // B - Stronger Yellow
        '#DC2626', // C - Stronger Red
        '#7C3AED', // D - Strong Purple
        '#374151'  // Fail - Darker Gray
      ],
      borderWidth: 0,
    }]
  }

  // Enhanced topic access data with more metrics
  const topicAccessData = [
    { 
      id: 1, 
      name: 'Machine Learning Basics', 
      accessCount: 120, 
      trend: 'up',
      avgTimeSpent: '45 mins',
      completionRate: '88%',
      difficulty: 'Medium'
    },
    { 
      id: 2, 
      name: 'Data Structures', 
      accessCount: 95, 
      trend: 'down',
      avgTimeSpent: '60 mins',
      completionRate: '75%',
      difficulty: 'High'
    },
    { 
      id: 3, 
      name: 'Deep Learning Fundamentals', 
      accessCount: 78, 
      trend: 'up',
      avgTimeSpent: '30 mins',
      completionRate: '92%',
      difficulty: 'Medium'
    },
    { 
      id: 4, 
      name: 'Cloud Computing', 
      accessCount: 60, 
      trend: 'down',
      avgTimeSpent: '40 mins',
      completionRate: '70%',
      difficulty: 'Medium'
    },
    { 
      id: 5, 
      name: 'Cybersecurity Essentials', 
      accessCount: 130, 
      trend: 'up',
      avgTimeSpent: '55 mins',
      completionRate: '85%',
      difficulty: 'High'
    },
    { 
      id: 6, 
      name: 'Operating Systems', 
      accessCount: 88, 
      trend: 'down',
      avgTimeSpent: '50 mins',
      completionRate: '78%',
      difficulty: 'High'
    }
  ]

  // Enhanced KPIs with more metrics
  const kpis = [
    {
      label: 'Total Enrollment',
      value: courseEnrollmentData.datasets[0].data.reduce((a, b) => a + b, 0),
      trend: 8,
      icon: 'users',
      subtext: 'Across all courses'
    },
    {
      label: 'Average Grade',
      value: 'B+',
      trend: 5,
      icon: 'chart-bar',
      subtext: 'Up from B last term'
    },
    {
      label: 'Course Completion',
      value: '92%',
      trend: 3,
      icon: 'check-circle',
      subtext: 'Target: 95%'
    },
    {
      label: 'Active Participation',
      value: '85%',
      trend: -2,
      icon: 'activity',
      subtext: 'Last 7 days'
    }
  ]

  // Enhanced performance metrics
  const performanceMetrics = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
    datasets: [
      {
        label: 'Assignment Scores',
        data: [85, 88, 82, 90, 87, 92],
        borderColor: '#DC2626',
        backgroundColor: 'rgba(220, 38, 38, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Quiz Scores',
        data: [78, 82, 85, 80, 88, 85],
        borderColor: '#2563EB',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Participation Score',
        data: [90, 85, 88, 92, 89, 94],
        borderColor: '#059669',
        backgroundColor: 'rgba(5, 150, 105, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  }

  // New: Student engagement patterns
  const engagementPatterns = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Active Hours',
      data: [6.5, 7.2, 5.8, 6.9, 4.5, 3.2, 2.8],
      backgroundColor: '#DC2626',
      borderRadius: 6,
    }]
  }

  // New: Resource utilization
  const resourceUtilization = {
    labels: ['Video Lectures', 'Practice Problems', 'Reading Materials', 'Discussion Forums', 'Live Sessions'],
    datasets: [{
      data: [45, 25, 15, 10, 5],
      backgroundColor: [
        '#2563EB',
        '#059669',
        '#D97706',
        '#DC2626',
        '#7C3AED'
      ],
      borderWidth: 0,
    }]
  }

  return {
    kpis,
    courseEnrollmentData,
    gradeDistributionData,
    topicAccessData,
    performanceMetrics,
    engagementPatterns,
    resourceUtilization,
    courseInfo: {
      name: filters.course,
      year: filters.year,
      term: filters.term
    }
  }
}

// Enhanced AI insights generator with more detailed analysis
const generateMockInsights = (data) => {
  const insights = [
    {
      title: 'Enrollment Pattern Analysis',
      description: 'ST has the highest enrollment (110 students) while SE shows lower numbers (78 students). Consider investigating factors affecting SE enrollment.',
      type: 'enrollment',
      severity: 'medium',
      recommendation: 'Review SE course marketing and prerequisites'
    },
    {
      title: 'Grade Distribution Insight',
      description: '60% of students achieved S or A grades, showing strong overall performance. However, there\'s a 3% failure rate that needs attention.',
      type: 'grades',
      severity: 'low',
      recommendation: 'Implement early warning system for struggling students'
    },
    {
      title: 'Topic Engagement Trends',
      description: 'Cybersecurity Essentials shows highest engagement (130 accesses). Cloud Computing needs more student engagement strategies.',
      type: 'engagement',
      severity: 'high',
      recommendation: 'Add more interactive content to Cloud Computing module'
    },
    {
      title: 'Performance Correlation',
      description: 'Assignment scores show consistent improvement over weeks. Quiz performance fluctuates - consider reviewing quiz difficulty levels.',
      type: 'performance',
      severity: 'medium',
      recommendation: 'Standardize quiz difficulty across weeks'
    },
    {
      title: 'Resource Utilization Analysis',
      description: 'Video lectures are most popular (45% usage), while live sessions show low participation (5%).',
      type: 'resources',
      severity: 'high',
      recommendation: 'Reschedule live sessions to better match student availability'
    },
    {
      title: 'Weekly Engagement Pattern',
      description: 'Peak activity on Tuesdays (7.2 hours), significant drop on weekends.',
      type: 'timing',
      severity: 'medium',
      recommendation: 'Consider scheduling key activities mid-week'
    }
  ]

  return insights
}

export const mockAnalyticsService = {
  getFacultyAnalytics: async (filters) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    return generateMockData(filters)
  },

  getAIInsights: async (data) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800))
    return generateMockInsights(data)
  },

  exportAnalytics: async (format, filters) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Create a mock file for download
    const mockData = generateMockData(filters)
    const content = JSON.stringify(mockData, null, 2)
    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/csv' })
    return blob
  }
} 