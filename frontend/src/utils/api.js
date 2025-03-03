import axios from "axios";

const apiUrl = "http://localhost:8000";
const apiPrefix = "api/v1";

const api = axios.create({
    baseURL: `${apiUrl}/${apiPrefix}`,
    headers: {
        "Content-Type": "application/json",
    },
});

console.log("Axios Base URL:", api.defaults.baseURL);

export default api;
