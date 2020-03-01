import axios from 'axios';
export let isCancel = axios.isCancel;

export function cancel(source) {
  if (source) { source.cancel('Cancelled request'); }
  return axios.CancelToken.source();
}

export const Budget = {
  getAccounts() { return axios.get('/api/budget/accounts'); },
  getCategories() { return axios.get('/api/budget/categories'); },
  getTransactions(params, cancelToken) { return axios.get('/api/budget/transactions', {params, cancelToken}); },
  getKeyVals() { axios.get('/api/budget/keyval'); },
  patchTransaction(id, data) { return axios.patch(`/api/budget/transactions/${id}`, data); },
  upload(formdata) { return axios.put('/api/budget/upload', formdata); },
};

export const Notes = {
  getNote(id) { return axios.get(`/api/notes/${id}`); },
  getNotes(params, cancelToken) { return axios.get('/api/notes', {params, cancelToken}); },
  saveNote(id, data) { return axios.put(`/api/notes/${id}`, data); },
};

export const Tools = {
  getEvents() { return axios.get(`/api/tools/events`); },
  getNews() { return axios.get(`/api/tools/news`); },
  getPhoto() { return axios.get(`/api/tools/photo`); },
  getTasks() { return axios.get(`/api/tools/tasks`); },
  getWeather() { return axios.get(`/api/tools/weather`); },
};

export const Users =  {
  getCurrentUser() { return axios.get('/api/user'); },
  login(data) { return axios.post('/api/user/login', data); },
  logout() { return axios.post('/api/user/logout'); },
  generateToken() { return axios.post('/api/user/gentoken'); },
};
