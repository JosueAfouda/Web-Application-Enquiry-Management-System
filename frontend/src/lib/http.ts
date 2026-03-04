import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export const http = axios.create({
  baseURL,
  timeout: 20000,
})

http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})
