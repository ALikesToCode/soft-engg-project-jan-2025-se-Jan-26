/**
 * Course model representing a course in the application
 * 
 * This class encapsulates course data and provides methods to access
 * course properties in a controlled manner.
 */
export class Course {
    /**
     * Creates a new Course instance with optional parameters
     * 
     * @param {object} options - Course properties (optional)
     * @param {string} [options.id] - Unique identifier for the course
     * @param {string} [options.title="Untitled Course"] - Title of the course
     * @param {string} [options.description="No description available"] - Description of the course
     * @param {string} [options.status="inactive"] - Status of the course (active, inactive)
     * @param {number} [options.progress=0] - Progress of the course (in percentage)
     * @param {string} [options.duration="Unknown"] - Duration of the course (e.g., "8 weeks")
     * @param {number} [options.studentsCount=0] - Number of students enrolled in the course
     * @param {object} [options.instructor={ name: "Unknown", avatar: "" }] - Instructor details
     */
    constructor({
        id = null,
        title = "Untitled Course",
        description = "No description available",
        status = "inactive",
        progress = 0,
        level = 'Beginner',
        is_bookmarked = true,
        duration = "Unknown",
        studentsCount = 0,
        instructor = { name: "Unknown", avatar: "" },
        image = 'https://placehold.co/400x300'
    } = {}) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.status = status;
        this.level = level;
        this.isBookmarked = is_bookmarked;
        this.progress = progress;
        this.duration = duration;
        this.studentsCount = studentsCount;
        this.instructor = instructor;
        this.image = image
    }

    /**
     * Gets the course title
     * @returns {string} The course's title
     */
    getTitle() {
        return this.title;
    }

    /**
     * Gets the course description
     * @returns {string} The course's description
     */
    getDescription() {
        return this.description;
    }

    /**
     * Gets the course status
     * @returns {string} The course's status (active, inactive)
     */
    getStatus() {
        return this.status;
    }

    /**
     * Gets the course progress
     * @returns {number} The course's progress percentage
     */
    getProgress() {
        return this.progress;
    }

    /**
     * Gets the course duration
     * @returns {string} The course duration (e.g., "8 weeks")
     */
    getDuration() {
        return this.duration;
    }

    /**
     * Gets the number of students enrolled in the course
     * @returns {number} The number of students in the course
     */
    getStudentsCount() {
        return this.studentsCount;
    }

    /**
     * Gets the instructor details
     * @returns {object} The instructor's details (name, avatar)
     */
    getInstructor() {
        return this.instructor;
    }

    /**
     * Sets the course's progress
     * @param {number} progress - The new progress percentage
     */
    setProgress(progress) {
        this.progress = progress;
    }

    /**
     * Sets the course's status
     * @param {string} status - The new status of the course
     */
    setStatus(status) {
        this.status = status;
    }


}
