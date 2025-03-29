import { defineStore } from 'pinia';
import { ref, onMounted, watch } from 'vue';
import FetchFunction from '../utils/FetchFunction';
import router from '../router/index';
import { User } from '@/models/User';
import { APP_BASE_URL, ROLE } from '@/AppConstants/globalConstants';
import { authService } from '@/api/authService';

// For development only - remove in production
const DEV_MODE = import.meta.env.VITE_NODE_ENV === 'development';

export default defineStore('auth', () => {
    // Parse token from localStorage, handling both string and JSON string formats
    const storedToken = localStorage.getItem('token');
    let parsedToken = null;

    try {
        // Try to parse as JSON first
        parsedToken = storedToken ? JSON.parse(storedToken) : null;
    } catch (e) {
        // If not valid JSON, use as is
        parsedToken = storedToken;
    }

    const token = ref(parsedToken);
    const returnUrl = ref(null);
    const user = ref(new User(null, "", "", ""));
    const userRole = ref(localStorage.getItem('userRole') || ROLE.STUDENT);
    const isAdmin = ref(false);
    const isDevelopment = ref(DEV_MODE);
    const hasPassword = ref(false);
    const isInitialized = ref(false);

    // Initialize auth state when store is created
    async function initialize() {
        console.log("Initializing auth store");
        
        if (isInitialized.value) {
            console.log("Auth store already initialized");
            return;
        }
        
        // Check if we have a token
        if (!token.value) {
            console.log("No token found, skipping initialization");
            isInitialized.value = true;
            return;
        }
        
        try {
            // Get user data
            const userData = await authService.getCurrentUser();
            if (userData) {
                setUser(userData);
                console.log(`Auth store initialized for user: ${userData.email}, role: ${userData.role}`);
            } else {
                console.warn("Failed to get user data during initialization");
                // Keep the token in case it's valid but the API call failed
            }
        } catch (error) {
            console.error("Error initializing auth store:", error);
            // Clear auth data on critical errors
            if (error.response && error.response.status === 401) {
                logout();
            }
        } finally {
            isInitialized.value = true;
        }
    }

    // Development only - helper to switch roles
    function switchRole(role) {
        if (!isDevelopment.value) return;
        if (Object.values(ROLE).includes(role)) {
            setUserRole(role);
            // Don't redirect, let the router handle navigation
        }
    }

    async function login(email, pswd) {
        if (isDevelopment.value) {
            // For development, just set a dummy token and keep current role
            token.value = "dummy-token";
            localStorage.setItem('token', JSON.stringify(token.value));

            // Navigate based on current role
            navigateToRoleDashboard();
            return;
        }

        try {
            const data = await FetchFunction({
                url: `${APP_BASE_URL}/${user}`,
                init_obj: {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    method: 'POST',
                    body: JSON.stringify(user),
                }
            }).catch((err) => {
                throw new Error("Error = " + err);
            })
            if (data) {
                token.value = data.response.user.authentication_token;
                setUserRole(data.role);
                localStorage.setItem('token', JSON.stringify(token.value));
                navigateToRoleDashboard();
                console.log(data)
            }
        } catch (error) {
            console.log("error = " + error);
            router.push({ path: '/', query: { error: 'true' } });
        }
    }

    // Helper method to navigate based on role
    function navigateToRoleDashboard() {
        switch (userRole.value) {
            case ROLE.STUDENT:
                router.push('/user/dashboard');
                break;
            case ROLE.FACULTY:
                router.push('/faculty/dashboard');
                break;
            case ROLE.SUPPORT:
                router.push('/support/dashboard');
                break;
            default:
                router.push('/');
        }
    }

    function logout() {
        user.value = null;
        token.value = null;
        userRole.value = ROLE.STUDENT;
        hasPassword.value = false;
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        router.push('/login');
    }

    function setUser(userData) {
        user.value.id = userData.id;
        user.value.name = userData.name;
        user.value.email = userData.email;
        user.value.role = userData.role;
        hasPassword.value = userData.has_password || false;
        setUserRole(userData.role);
    }

    function setUserRole(role) {
        if (role && typeof role === 'string') {
            // Normalize role to uppercase
            const normalizedRole = role.toUpperCase();
            
            // Validate against known roles
            if (Object.values(ROLE).includes(normalizedRole)) {
                userRole.value = normalizedRole;
                localStorage.setItem('userRole', normalizedRole);
                console.log(`User role set to: ${normalizedRole}`);
            } else {
                console.warn(`Invalid role: ${role}, defaulting to STUDENT`);
                userRole.value = ROLE.STUDENT;
                localStorage.setItem('userRole', ROLE.STUDENT);
            }
        } else {
            console.warn(`Invalid role value: ${role}, defaulting to STUDENT`);
            userRole.value = ROLE.STUDENT;
            localStorage.setItem('userRole', ROLE.STUDENT);
        }
    }

    function clearUser() {
        user.value = new User(null, "", "", "");
        userRole.value = ROLE.STUDENT;
        hasPassword.value = false;
        localStorage.removeItem('userRole');
    }

    // Check if the current user needs to set a password
    async function checkPasswordStatus() {
        try {
            const userData = await authService.getCurrentUser();
            if (userData) {
                hasPassword.value = userData.has_password || false;
                return hasPassword.value;
            }
            return false;
        } catch (error) {
            console.error('Error checking password status:', error);
            return false;
        }
    }

    // Set password for the current user
    async function setPassword(password) {
        try {
            const result = await authService.setPassword(password);
            if (result.success) {
                hasPassword.value = true;
            }
            return result;
        } catch (error) {
            console.error('Error setting password:', error);
            return { success: false, message: 'Failed to set password' };
        }
    }

    // Initialize the store on creation
    // Note: This is called when the store is first accessed
    setTimeout(initialize, 0);

    return {
        token,
        returnUrl,
        user,
        userRole,
        isAdmin,
        isDevelopment,
        hasPassword,
        isInitialized,
        initialize,
        switchRole,
        login,
        logout,
        setUser,
        setUserRole,
        clearUser,
        navigateToRoleDashboard,
        checkPasswordStatus,
        setPassword
    };
});