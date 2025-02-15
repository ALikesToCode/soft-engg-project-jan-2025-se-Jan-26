const formatDateFunc = (date) => {
    const d = new Date(date)
    if (isNaN(d.getTime())) {
        throw new Error("Invalid date format");
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