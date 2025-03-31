const formatDateFunc = (date) => {
    // Check for null or undefined
    if (date === null || date === undefined) {
        return 'N/A';
    }
    
    const d = new Date(date);
    if (isNaN(d.getTime())) {
        console.warn("Invalid date format:", date);
        return 'Invalid date';
    }
    
    const months = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    ]
    const month = months[d.getMonth()]
    const day = d.getDate()
    const year = d.getFullYear()
    const hours = d.getHours()
    const minutes = d.getMinutes().toString().padStart(2, '0')
    const ampm = hours >= 12 ? 'PM' : 'AM'
    const formattedHours = hours % 12 || 12

    return `${month} ${day}, ${year} ${formattedHours}:${minutes} ${ampm}`
}

export default formatDateFunc;