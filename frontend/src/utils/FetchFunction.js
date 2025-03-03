async function fetchFunction({ url, init_obj, authTokenReq }) {

    if (url === undefined) {
        throw new Error("Url is required")
    }
    if (init_obj === undefined) {
        init_obj = {}
    }
    if (authTokenReq === undefined) {
        authTokenReq = false
    }
    if (authTokenReq === true) {
        const token = localStorage.getItem('token');
        if (init_obj.headers === undefined) {
            init_obj.headers = {
                'Authorization': `Bearer ${token}`,
            }
        }
        else {
            init_obj.headers['Authorization'] = `Bearer ${token}`
        }
    }
    const response = await fetch(url, init_obj).catch(() => { 
        throw new Error("Network Error")
    })

    if (response) {
        if (response.ok) {
            const data = await response.json().catch(() => {
                throw new Error("Unexpected Respone. Must be json")
            })
            if (data) {
                return data
            }
        }
        else {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
    }
    else {
        console.log("No respone from the server")
    }
}
export default fetchFunction