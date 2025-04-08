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
  // Budget Accounts
  listAccounts(params, signal) { return axios.get(`/api/budget/accounts`, {params, signal}) },
  getAccount(accountid, params, signal) { return axios.get(`/api/budget/accounts/${accountid}`, {params, signal}) },
  updateAccount(accountid, data, signal) { return axios.patch(`/api/budget/accounts/${accountid}`, data, {signal}) },
  deleteAccount(accountid, signal) { return axios.delete(`/api/budget/accounts/${accountid}`, {signal}) },
  sortAccounts(data, signal) { return axios.patch(`/api/budget/sort_accounts`, data, {signal}) },
  // Budget Categories
  getCategories(params, signal) { return axios.get(`/api/budget/categories`, {params, signal}) },
  getCategory(categoryid, params, signal) { return axios.get(`/api/budget/categories/${categoryid}`, {params, signal}) },
  sortCategories(data, signal) { return axios.patch(`/api/budget/sort_categories`, data, {signal}) },
  // Budget Transactions
  getTransactions(params, signal) { return axios.get(`/api/budget/transactions`, {params, signal}) },
  getTransaction(transactionid, params, signal) { return axios.get(`/api/budget/transactions/${transactionid}`, {params, signal}) },
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
