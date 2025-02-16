// Layout configuration settings
export const LAYOUT_CONFIG = {
    // Navbar heights
    MAIN_NAVBAR_HEIGHT: '4rem', // 64px
    
    // Sidebar configuration
    SIDEBAR: {
        DEFAULT_WIDTH: '16',      // 64px (collapsed)
        EXPANDED_WIDTH: '48',    // 192px (expanded)
        TRANSITION_DURATION: '300',
        BACKGROUND: {
            FROM: 'maroon-800',
            TO: 'maroon-600'
        }
    },

    // Role switcher configuration
    ROLE_SWITCHER: {
        MAX_HEIGHT: '120px',
        POSITION: {
            BOTTOM: '4',
            RIGHT: '4'
        }
    },

    // Scrollbar configuration
    SCROLLBAR: {
        HIDE: true
    },

    // Animation configuration
    ANIMATIONS: {
        TRANSITION_TIMING: 'ease-in-out',
        HOVER_SCALE: '110'
    }
}

// Icon configuration
export const ICON_CONFIG = {
    DEFAULT_SIZE: '24px',
    VARIATION_SETTINGS: {
        FILL: 0,
        WEIGHT: 400,
        GRADE: 0,
        OPTICAL_SIZE: 24
    }
}

// Role icons mapping using correct Material Symbols names
export const ROLE_ICONS = {
    STUDENT: 'school',
    FACULTY: 'history_edu',
    SUPPORT: 'support_agent',
    DEFAULT: 'person'
} 