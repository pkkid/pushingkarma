import axios from 'axios'
import {ref} from 'vue'
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

// Get (wrapper)
// Wrapping the axios.get method to save the latest GET request URL. This
// allows the API button in the navigation to show the latest request.
export const apidocurl = ref('/apidoc')
async function get(url, config) {
  var params = config.params || {}
  params = Object.keys(params).map(function(key) { return `${key}=${params[key] || ''}` }).join('%26')
  apidocurl.value = params ? `/apidoc?view=/api${url}?${params}` : `/apidoc?view=/api${url}`
  return axios.get(url, config)
}

// Api Endpoints
// Endpoints defined in the Django application
export const Main = {
  generateToken(signal) { return axios.post(`/main/generate_token`, null, {signal}) },
  getCurrentUser(signal) { return get(`/main/user`, {signal}) },
  getGlobalVars(signal) { return get(`/main/global_vars`, {signal}) },
  login(data, signal) { return axios.post(`/main/login`, data, {signal}) },
  logout(signal) { return axios.post(`/main/logout`, null, {signal}) },
}
export const Budget = {
  getAccounts(params, signal) { return get(`/budget/accounts`, {params, signal}) },
  getCategories(params, signal) { return get(`/budget/categories`, {params, signal}) },
  getTransactions(params, signal) { return get(`/budget/transactions`, {params, signal}) },
}
export const Obsidian = {
  getNote(params, signal) { return get(`/obsidian/note`, {params, signal}) },
  search(params, signal) { return get(`/obsidian/search`, {params, signal}) },
}
export const Stocks = {
  getTickers(params, signal) { return get(`/stocks/tickers`, {params, signal}) },
  projectionTrends(params, signal) { return get(`/stocks/projection_trends`, {params, signal}) },
}
