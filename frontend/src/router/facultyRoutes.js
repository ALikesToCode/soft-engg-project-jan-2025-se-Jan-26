import ContentUpload from '../views/faculty/ContentUpload.vue'
import FacultyDashboard from '../views/faculty/FacultyDashboard.vue'
import FacultyDetails from '../views/faculty/FacultyDetails.vue'

const facultyRoutes =   {
    path: '/faculty',
    name: 'facultyDashboard',
    children: [
        {
            path: 'dashboard',
            component: FacultyDashboard,
            meta: {
                title: 'Faculty Dashboard'
            }
        },
        {
            path: 'content-upload',
            component: ContentUpload,
            meta: {
                title: 'Content Upload'
            }
        },
        {
            path: 'details',
            component: FacultyDetails,
            meta: {
                title: 'User Details'
            }
        },
    ]
};

export default facultyRoutes;