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
  var payload = (method == axios.get) ? {params:vars} : {data:vars};
  var promise = method(url, {
    ...payload,
    headers: {'X-CSRFToken': Cookie.get('csrftoken')},
    cancelToken: new axios.CancelToken(function executor(c) { cancel = c; }),
  });
  var {data} = await promise;
  return {data, promise, cancel};
}

export const UsersAPI =  {
  user()         { return makeRequest(axios.get, `/api/user`); },
  login(payload) { return makeRequest(axios.post, `/api/user/login`, payload); },
  logout()       { return makeRequest(axios.post, `/api/user/logout`); },
  gentoken()     { return makeRequest(axios.post, `/api/user/gentoken`); },
};

export const NotesAPI = {
  note(id)       { return makeRequest(axios.get, `/api/notes/${id}`); },
  notes(payload) { return makeRequest(axios.get, `/api/notes`, payload); },
};

export const BudgetAPI = {
  ACCOUNTS: '/api/accounts',
  UPLOAD: '/api/transactions/upload',
};


