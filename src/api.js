import axios from 'axios';
export let isCancel = axios.isCancel;

export function cancel(source) {
  if (source) { source.cancel('Cancelled request'); }
  return axios.CancelToken.source();
}

export const UsersAPI =  {
  getCurrentUser() { return axios.get('/api/user'); },
  login(data) { return axios.post('/api/user/login', data); },
  logout() { return axios.post('/api/user/logout'); },
  generateToken() { return axios.post('/api/user/gentoken'); },
};

export const NotesAPI = {
  getNote(id) { return axios.get(`/api/notes/${id}`); },
  saveNote(id, data) { return axios.put(`/api/notes/${id}`, data); },
  listNotes(params, cancelToken) { return axios.get('/api/notes', {params, cancelToken}); },
};

export const BudgetAPI = {
  listAccounts() { return axios.get('/api/accounts'); },
  listCategories() { return axios.get('/api/categories'); },
  listTransactions(params, cancelToken) { return axios.get('/api/transactions', {params, cancelToken}); },
  listKeyVals() { axios.get('/api/keyval'); },
  upload(data) { return axios.put('/api/transactions/upload', {data}); },
};


