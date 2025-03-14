import axios from 'axios'
import * as utils from '@/utils/utils'
export const isCancel = axios.isCancel

// Configure Axios CSRF Token and baseURL
// https://axios-http.com/docs/req_config
axios.defaults.withCredentials = true
axios.defaults.withXSRFToken = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.baseURL = utils.apibase
console.debug(`Axios.defaults.baseURL: ${axios.defaults.baseURL}`)

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
export const Obsidian = {
  getNote(params, signal) { return axios.get(`/obsidian/note`, {params, signal}) },
  search(params, signal) { return axios.get(`/obsidian/search`, {params, signal}) },
}
export const Stocks = {
  getTickers(params, signal) { return axios.get(`/stocks/tickers`, {params, signal}) },
  projectionTrends(params, signal) { return axios.get(`/stocks/projection_trends`, {params, signal}) },
}
