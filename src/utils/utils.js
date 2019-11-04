import axios from 'axios';
import Cookie from "js-cookie";
export {axios};


/**
 * Cancel
 * Cancel the specified request
 */
export function cancel(request) {
  if (request) { request.cancel(); }
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
 * Insert Commas
 * Add commas to the specified number.
 */
export function insertCommas(value) {
  var parts = value.toString().split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}


/**
 * Make Request
 * Run the specified request and return the result.
 *   method - Method to request axios.get, axios.post, axios.put, etc..
 *   url - URL to send this request.
 *   vars - Object of key->value pairs to replace in the query string.
 */
export function makeRequest(method, url, vars) {
  url = sfmt(url, vars);
  let cancel;
  if (method == axios.get) { vars = {params: vars}; }
  let xhr = method(url, vars, {
    cancelToken: new axios.CancelToken(function executor(c) { cancel = c; }),
    headers: {'X-CSRFToken': Cookie.get('csrftoken')},
  });
  return {xhr, cancel};
}


/**
 * Keep In Range
 * Make sure the specified value is within min and max (inclusive).
 */
export function keepInRange(value, min, max) {
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
