/**
 * User model representing a user in the application
 * 
 * This class encapsulates user data and provides methods to access
 * user properties in a controlled manner.
 */
export class User {
    /**
     * Creates a new User instance
     * 
     * @param {string} id - Unique identifier for the user
     * @param {string} name - User's display name
     * @param {string} email - User's email address
     * @param {string} role - User's role (student, faculty, or support)
     */
    constructor(id, name, email, role) {
      this.id = id;
      this.name = name;
      this.email = email;
      this.role = role;
    }  

    /**
     * Gets the user's display name
     * 
     * @returns {string} The user's name
     */
    getName() {
      return this.name;
    }

    /**
     * Gets the user's email address
     * 
     * @returns {string} The user's email
     */
    getEmail() {
        return this.email;
    }

    /**
     * Gets the user's role
     * 
     * @returns {string} The user's role (student, faculty, or support)
     */
    getRole() {
        return this.role;
    }

    /**
     * Checks if the user has a specific role
     * 
     * @param {string} roleToCheck - The role to check against
     * @returns {boolean} True if the user has the specified role, false otherwise
     */
    hasRole(roleToCheck) {
        return this.role === roleToCheck;
    }
  }
  