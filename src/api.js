import axios from 'axios';
import Cookie from "js-cookie";

/**
 * Make Request
 * Run the specified request and return the result.
 *   method - Method to request axios.get, axios.post, axios.put, etc..
 *   url - URL to send this request.
 *   vars - Object of key->value pairs to replace in the query string.
 */
export async function makeRequest(method, url, vars) {
  var cancel;
  var payload = (method == 'get') ? {params:vars} : {data:vars};
  var promise = axios({method, url, ...payload,
    headers: {'X-CSRFToken': Cookie.get('csrftoken')},
    cancelToken: new axios.CancelToken(function executor(c) { cancel = c; }),
  });
  var {data} = await promise;
  return {data, promise, cancel};
}

export const UsersAPI =  {
  getCurrentUser() { return makeRequest('get', `/api/user`); },
  login(data) { return makeRequest('post', `/api/user/login`, data); },
  logout() { return makeRequest('post', `/api/user/logout`); },
  generateToken() { return makeRequest('post', `/api/user/gentoken`); },
};

export const NotesAPI = {
  note(id) { return makeRequest('get', `/api/notes/${id}`); },
  notes(params) { return makeRequest('get', `/api/notes`, params); },
};

export const BudgetAPI = {
  ACCOUNTS: '/api/accounts',
  UPLOAD: '/api/transactions/upload',
};


