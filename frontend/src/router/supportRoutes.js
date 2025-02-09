import SupportDashboard from '../views/support/SupportDashboard.vue'


const supportRoutes = {
    path: '/support',
    name: 'supportDashboard',
    children: [
        {
            path: 'dashboard',
            component: SupportDashboard,
            meta: {
                title: 'Support Dashboard',
                hideNavbar: true,
                hideFooter: true,
            }
        }
    ]
};

export default supportRoutes;