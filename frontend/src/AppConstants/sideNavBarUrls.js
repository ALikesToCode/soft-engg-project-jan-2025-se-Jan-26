const studentDashboardUrls = [
    {
        path: '/user/dashboard',
        icon: 'dashboard',
        label: 'Dashboard'
    },
    {
        path: '/user/courses',
        icon: 'auto_stories',
        label: 'Courses'
    },
    {
        path: '/user/course-history',
        icon: 'history',
        label: 'History'
    }
]
const facultyDashboardUrls = [
    {
        path: '/faculty/dashboard',
        icon: 'dashboard',
        label: 'Dashboard'
    },
    {
        path: '/faculty/notifications',
        icon: 'campaign',
        label: 'Send Notifications'
    },
    {
        path: '/faculty/content-upload',
        icon: 'upload',
        label: 'Upload Content'
    },
    {
        path: '/faculty/academic-integrity',
        icon: 'gavel',
        label: 'Academic Integrity'
    },
    {
        path: '/faculty/course/enrollment',
        icon: 'group',
        label: 'Course Enrollment'
    }
]
const supportDashboardUrls = [
    {
        path: '/support/dashboard',
        icon: 'dashboard',
        label: 'Dashboard'
    },
    {
        path: '/support/notifications',
        icon: 'campaign',
        label: 'Send Notifications'
    },
    {
        path: '/support/faq-management',
        icon: 'help_center',
        label: 'FAQ Management'
    },
    {
        path: '/support/user-management',
        icon: 'manage_accounts',
        label: 'User Management',
        requiresAdmin: true
    },
    {
        path: '/support/course-assignments',
        icon: 'school',
        label: 'Course Assignments',
        requiresAdmin: true
    },
    {
        path: '/support/system-settings',
        icon: 'settings',
        label: 'System Settings',
        requiresAdmin: true
    }
]

export { studentDashboardUrls, facultyDashboardUrls, supportDashboardUrls };
