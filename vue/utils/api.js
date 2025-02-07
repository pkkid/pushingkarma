import axios from 'axios'
import * as utils from '@/utils/utils'

export const isCancel = axios.isCancel
axios.defaults.baseURL = utils.apibase
axios.defaults.withCredentials = true
console.debug(`Axios.defaults.baseURL: ${axios.defaults.baseURL}`)

// Cancel
// Cancel a previously started request
export function cancel(controller) {
  if (controller) { controller.abort('Cancelled request') }
  return new AbortController()
}

export const Main = {
  genToken(signal) { return axios.post(`/main/gentoken`, {signal}) },
  getCurrentUser(signal) { return axios.get(`/main/user`, {signal}) },
  getGlobalVars(signal) { return axios.get(`/main/globalvars`, {signal}) },
  login(data, signal) { return axios.post(`/main/login`, data, {signal}) },
  logout(signal) { return axios.post(`/main/logout`, {signal}) },
}