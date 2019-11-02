import axios from 'axios';
import Cookie from "js-cookie";

export {axios};

/**
 * Build Query
 * Run the specified GraphQL query and return the result
 *   query - Query to run with vars specified by brackets {var}.
 *   vars - Object of key->value pairs to replace in the query string.
 *   ctoken - Axios cancelToken to manipulate manage for aborts.
 */
export function buildquery(querytmpl, vars) {
  let cancel;
  let query = sfmt(querytmpl, vars);
  let url = _appendQueryMethod('/graphql', query);
  let xhr = axios.post(url, {query}, {
    cancelToken: new axios.CancelToken(function executor(c) { cancel = c; }),
    headers: {'X-CSRFToken': Cookie.get('csrftoken')},
  });
  return {xhr, cancel};
}

function _appendQueryMethod(url, query) {
  // Try to parse the method call from the specified query.
  let result = query.replace(/\n/g, '').match(/\{\s*(.*?)\s*[\\{\\(]/i);
  if (result && result.length == 2) { url += '/'+result[1]; }
  return url;
}


/**
 * Make Request
 * Run the specified request and return the result.
 */
export function makeRequest(method, url, data) {
  let cancel;
  let xhr = method(url, data, {
    cancelToken: new axios.CancelToken(function executor(c) { cancel = c; }),
    headers: {'X-CSRFToken': Cookie.get('csrftoken')},
  });
  return {xhr, cancel};
}


/**
 * Contains - Return a list of items contianing the specified pattern.
 *   selector - Base querySelector input to find items to search.
 *   regex - Regex to compare the contents of each found item.
 */
export function contains(selector, regex) {
  var elems = document.querySelectorAll(selector);
  var results = Array.prototype.filter.call(elems, function(elem) {
    return RegExp(regex, 'i').test(elem.textContent);
  });
  return results.length ? results[0] : null;
}

/**
 * minmax
 * Make sure the specified value is within min and max (inclusive).
 */
export function minmax(value, min, max) {
  value = Math.max(value, min);
  return Math.min(value, max);
}

/**
 * String Format
 * Format the specified template with the key/value object mapping.
 *   str - String to format with vars specified by brackets {var}.
 *   vars - Object of key->value pairs to replace in the template string.
 */
export function sfmt(str, vars) {
  for (let key in vars) {
    str = str.replace(`{${key}}`, JSON.stringify(vars[key]), 'g');
  }
  return str;
}
