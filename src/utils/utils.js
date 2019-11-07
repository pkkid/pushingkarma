import * as _ from 'lodash';
import axios from 'axios';
export {axios};

// Cancel
// Cancel the specified request
export function cancel(request) {
  if (request) { request.cancel(); }
}

// Contains - Return a list of items contianing the specified pattern.
//   selector - Base querySelector input to find items to search.
//   regex - Regex to compare the contents of each found item.
export function contains(selector, regex) {
  var elems = document.querySelectorAll(selector);
  var results = Array.prototype.filter.call(elems, function(elem) {
    return RegExp(regex, 'i').test(elem.textContent);
  });
  return results.length ? results[0] : null;
}

// Find Index
// Find item in list of objects with the specified key/value.
export function findIndex(objs, key, value) {
  return objs.findIndex(function(item) {
    return item[key] == value;
  });
}

// Insert Commas
// Add commas to the specified number.
export function insertCommas(value) {
  var parts = value.toString().split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}

// Keep In Range
// Make sure the specified value is within min and max (inclusive).
export function keepInRange(value, min, max) {
  value = Math.max(value, min);
  return Math.min(value, max);
}

// Keep In View
// Scroll container to keep item in view within the specified margin.
export function keepInView(container, item, margin, behavior) {
  var scrollto;
  var itemtop = item.offsetTop;
  var itembottom = item.offsetTop + item.clientHeight;
  var scrolltop = container.scrollTop + margin;
  var scrollbottom = container.scrollTop + container.clientHeight - margin;
  if (itemtop < scrolltop) {
    scrollto = item.offsetTop - margin;
    container.scroll({top:scrollto, behavior:behavior});
  } else if (itembottom > scrollbottom) {
    scrollto = item.offsetTop - container.clientHeight + margin + item.clientHeight;
    container.scroll({top:scrollto, behavior:behavior});
  }
}

// String Format
// Format the specified template with the key/value object mapping.
//   str - String to format with vars specified by brackets {var}.
//   vars - Object of key->value pairs to replace in the template string.
export function sfmt(str, vars) {
  for (let key in vars) {
    str = str.replace(`{${key}}`, JSON.stringify(vars[key]), 'g');
  }
  return str;
}

// Update History
// Update the address bar history.
export function updateHistory(router, changes) {
  var query = {};
  var fullquery = Object.assign({}, router.history.current.query, changes);
  _.forOwn(fullquery, function(value, key) {
      if (value) { query[key] = value.toString(); }
  });
  if (!_.isEqual(query, router.history.current.query)) {
    router.push({query});
  }
  //query = _.pickBy(query, _.identity);  // remove falsey values
}
