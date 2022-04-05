import axios from 'axios';
export let isCancel = axios.isCancel;

export function cancel(source) {
  if (source) { source.cancel('Cancelled request'); }
  return axios.CancelToken.source();
}

export const Budget = {
  createAccount(data) { return axios.post(`/api/budget/accounts`, data); },
  createCategory(data) { return axios.post(`/api/budget/categories`, data); },
  deleteAccount(id) { return axios.delete(`/api/budget/accounts/${id}`); },
  deleteCategory(id) { return axios.delete(`/api/budget/categories/${id}`); },
  getAccounts() { return axios.get(`/api/budget/accounts`); },
  getCategories() { return axios.get(`/api/budget/categories`); },
  getHistory() { return axios.get(`/api/budget/history`); },
  getSummary() { return axios.get(`/api/budget/summary`); },
  getTransactions(params, cancelToken) { return axios.get(`/api/budget/transactions`, {params, cancelToken}); },
  getKeyVals() { axios.get(`/api/budget/keyval`); },
  patchAccount(id, data) { return axios.patch(`/api/budget/accounts/${id}`, data); },
  patchCategory(id, data) { return axios.patch(`/api/budget/categories/${id}`, data); },
  patchTransaction(id, data) { return axios.patch(`/api/budget/transactions/${id}`, data); },
  upload(formdata) { return axios.put(`/api/budget/upload`, formdata); },
};

export const Notes = {
  createNote(data) { return axios.post(`/api/notes`, data); },
  deleteNote(id) { return axios.delete(`/api/notes/${id}`); },
  getNote(id) { return axios.get(`/api/notes/${id}`); },
  getNotes(params, cancelToken) { return axios.get(`/api/notes`, {params, cancelToken}); },
  saveNote(id, data) { return axios.put(`/api/notes/${id}`, data); },
};

export const Tools = {
  getEvents() { return axios.get(`/api/tools/events`); },
  getNews() { return axios.get(`/api/tools/news`); },
  getPhoto() { return axios.get(`/api/tools/photo`); },
  getTasks() { return axios.get(`/api/tools/tasks`); },
  getWeather() { return axios.get(`/api/tools/weather`); },
  refreshPhoto() { return axios.get(`/api/tools/photo?force=1`); },
};

export const Users =  {
  getCurrentUser() { return axios.get(`/api/user`); },
  login(data) { return axios.post(`/api/user/login`, data); },
  generateToken() { return axios.post(`/api/user/gentoken`); },
  disconnect(provider) { return axios.post(`/api/user/disconnect`, {provider}); },
  logout() { return axios.post(`/api/user/logout`); },
};
