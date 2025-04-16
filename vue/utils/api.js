import axios from 'axios'
import * as utils from '@/utils/utils'
export const isCancel = axios.isCancel
export var history = []

// Configure Axios CSRF Token and baseURL
// https://axios-http.com/docs/req_config
axios.defaults.saveHistory = false
axios.defaults.withCredentials = true
axios.defaults.withXSRFToken = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.baseURL = utils.apibase
console.debug(`Axios.defaults.baseURL: ${axios.defaults.baseURL}`)

// API Endpoints
// Endpoints defined in the Django application
export const Main = {
  getGlobalVars(signal) { return axios.get(`/api/main/global_vars`, {signal}) },
  login(data, signal) { return axios.post(`/api/main/login`, data, {signal}) },
  logout(signal) { return axios.post(`/api/main/logout`, null, {signal}) },
}
export const Budget = {
  deleteAccount(pk, signal) { return axios.delete(`/api/budget/accounts/${pk}`, {signal}) },
  deleteCategory(pk, signal) { return axios.delete(`/api/budget/categories/${pk}`, {signal}) },
  getAccount(pk, params, signal) { return axios.get(`/api/budget/accounts/${pk}`, {params, signal}) },
  getCategory(pk, params, signal) { return axios.get(`/api/budget/categories/${pk}`, {params, signal}) },
  getTransaction(pk, params, signal) { return axios.get(`/api/budget/transactions/${pk}`, {params, signal}) },
  importTransactions(data, signal) { return axios.post(`/api/budget/import_transactions`, data, {signal}) },
  listAccounts(params, signal) { return axios.get(`/api/budget/accounts`, {params, signal}) },
  listCategories(params, signal) { return axios.get(`/api/budget/categories`, {params, signal}) },
  listTransactions(params, signal) { return axios.get(`/api/budget/transactions`, {params, signal}) },
  sortAccounts(data, signal) { return axios.patch(`/api/budget/sort_accounts`, data, {signal}) },
  sortCategories(data, signal) { return axios.patch(`/api/budget/sort_categories`, data, {signal}) },
  updateAccount(pk, data, signal) { return axios.patch(`/api/budget/accounts/${pk}`, data, {signal}) },
  updateCategory(pk, data, signal) { return axios.patch(`/api/budget/categories/${pk}`, data, {signal}) },
}
export const Obsidian = {
  getNote(bucket, path, params, signal) { return axios.get(`/api/obsidian/notes/${bucket}/${path}`, {params, signal}) },
  listNotes(params, signal) { return axios.get(`/api/obsidian/notes`, {params, signal}) },
}
export const Stocks = {
  getTicker(ticker, params, signal) { return axios.get(`/api/stocks/tickers/${ticker}`, {params, signal}) },
  listTickers(params, signal) { return axios.get(`/api/stocks/tickers`, {params, signal}) },
  chartRanks(params, signal) { return axios.get(`/api/stocks/chart_ranks`, {params, signal}) },
}

// Cancel
// Cancel a previously started request
export function cancel(controller) {
  if (controller) { controller.abort('Cancelled request') }
  return new AbortController()
}
