import UserDashboard from '../views/user/UserDashboard.vue'
import UserCourses from '../views/user/UserCourses.vue'
import UserDetails from '../views/user/UserDetails.vue'

const userRoutes =   {
    path: '/user',
    name: 'userDashboard',
    children: [
        {
            path: 'dashboard',
            component: UserDashboard,
            meta: {
                title: 'User Dashboard'
            }
        },
        {
            path: 'courses',
            component: UserCourses,
            meta: {
                title: 'User Courses'
            }
        },
        {
            path: 'details',
            component: UserDetails,
            meta: {
                title: 'User Details'
            }
        },
    ]
};

export default userRoutes;