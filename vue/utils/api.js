import axios from 'axios'
import * as utils from '@/utils/utils'

export const isCancel = axios.isCancel
axios.defaults.baseURL = utils.apibase
axios.defaults.withCredentials = true
console.debug(`Axios.defaults.baseURL: ${axios.defaults.baseURL}`)

// Add a request interceptor to include the CSRF token
axios.interceptors.request.use(config => {
  const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1]
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
}, error => {
  return Promise.reject(error)
})

// Cancel
// Cancel a previously started request
export function cancel(controller) {
  if (controller) { controller.abort('Cancelled request') }
  return new AbortController()
}

export const Main = {
  genToken(signal) { return axios.post(`/main/gentoken`, null, {signal}) },
  getCurrentUser(signal) { return axios.get(`/main/user`, {signal}) },
  getGlobalVars(signal) { return axios.get(`/main/globalvars`, {signal}) },
  login(data, signal) { return axios.post(`/main/login`, data, {signal}) },
  logout(signal) { return axios.post(`/main/logout`, null, {signal}) },
}