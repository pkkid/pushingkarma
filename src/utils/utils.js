import axios from 'axios';
import Cookie from "js-cookie";

/**
 * String Format - Format the specified template with the key/value object mapping.
 * @param str - String to format with vars specified by brackets {var}.
 * @param vars - Object of key->value pairs to replace in the template string.
 */
export function sfmt(str, vars) {
  for (let key in vars) {
    str = str.replace(`{${key}}`, JSON.stringify(vars[key]), 'g');
  }
  return str;
}

/**
 * Query - Run the specified GraphQL query and return the result
 * @param query - Query to run with vars specified by brackets {var}.
 * @param vars - Object of key->value pairs to replace in the query string.
 * @param ctoken - Axios cancelToken to manipulate manage for aborts.
 */
export function buildquery(query, vars) {
  let cancel;
  let xhr = axios.post('/graphql', {
    query: sfmt(query, vars),
  },{
    cancelToken: new axios.CancelToken(function executor(c) { cancel = c; }),
    headers: {'X-CSRFToken': Cookie.get('csrftoken')},
  });
  return {xhr, cancel};
}

/**
 * minmax - Make sure the specified value is within min and max (inclusive).
 */
export function minmax(value, min, max) {
  value = Math.max(value, min);
  return Math.min(value, max);
}
