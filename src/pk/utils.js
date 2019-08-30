import axios from 'axios';
const CancelToken = axios.CancelToken;

/**
 * String Format - Format the specified template with the key/value object mapping.
 * @param str - String to format with vars specified by brackets {var}.
 * @param vars - Object of key->value pairs to replace in the template string.
 */
export function sfmt(str, vars) {
  for (let key in vars) {
    str = str.replace(`{${key}}`, vars[key], 'g');
  }
  return str;
}

/**
 * Query - Run the specified GraphQL query and return the result
 * @param query - Query to run with vars specified by brackets {var}.
 * @param vars - Object of key->value pairs to replace in the query string.
 * @param ctoken - Axios cancelToken to manipulate manage for aborts.
 */
export function query(query, vars) {
  let cancel;
  let xhr = axios.post('/graphql', {
    query: sfmt(query, vars),
    variables: null
  },{
    cancelToken: new CancelToken(function executor(c) { cancel = c; })
  });
  return {xhr, cancel};
}
