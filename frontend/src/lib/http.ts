import axios from 'axios'

export const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export const http = axios.create({
  baseURL: apiBaseUrl,
  timeout: 20000,
})

http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})
