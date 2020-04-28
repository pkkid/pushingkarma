import * as dayjs from 'dayjs';
import axios from 'axios';
import forOwn from 'lodash/forOwn';
import isEqual from 'lodash/isEqual';
export {axios};
import {SnackbarProgrammatic as Snackbar} from 'buefy';

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

// Copy To Clipboard
// https://techoverflow.net/2018/03/30/copying-strings-to-the-clipboard-using-pure-javascript/
export function copyToClipboard(str) {
  var elem = document.createElement('textarea');
  elem.value = str;
  elem.setAttribute('readonly', '');
  elem.style = {position: 'absolute', left: '-9999px'};
  document.body.appendChild(elem);
  elem.select();
  document.execCommand('copy');
  document.body.removeChild(elem);
}

// Drag Type
// Returns 'file' or <tagname> of element being dragged.
export function dragType(event) {
  if (!event.dataTransfer) { return; }
  var dt = event.dataTransfer;
  if (dt.types && (dt.types.indexOf ? dt.types.indexOf('Files') != -1 : dt.types.contains('Files'))) {
    return 'file';
  }
  return 'element';
}

// ds2wuIcon
// DarkSky to WeatherUndereground icon translation
// Unused WU icons: chanceflurries, chancerain, chancesleet,
// chancesnow, chancetstorms, flurries, hazy, mostlycloudy,
// mostlysunny, partlysunny, sunny, tstorms
export function ds2wuIcon(dsicon) {
  var wuicon;
  dsicon = dsicon.replace('-day', '');
  dsicon = dsicon.replace('-night', '');
  switch(dsicon) {
    case 'clear': wuicon = 'clear'; break;
    case 'cloudy': wuicon = 'cloudy'; break;
    case 'fog': wuicon = 'fog'; break;
    case 'partly-cloudy': wuicon = 'partlycloudy'; break;
    case 'rain': wuicon = 'rain'; break;
    case 'sleet': wuicon = 'sleet'; break;
    case 'snow': wuicon = 'snow'; break;
    default: wuicon = 'unknown'; break;
  }
  return wuicon;
}

// Find Index
// Find item in list of objects with the specified key/value.
export function findIndex(objs, key, value) {
  return objs.findIndex(function(item) {
    return item[key] == value;
  });
}

// Format Date
// Wrapper around dayjs.format
// https://day.js.org/docs/en/display/format
export function formatDate(value, format) {
  return dayjs(value).format(format);
}

// Insert Commas
// Add commas to the specified number.
export function insertCommas(value) {
  var parts = value.toString().split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return parts.join('.');
}

// Int
// Wrapper around parseInt
export function int(value) {
  return parseInt(value, 10);
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

// Preload Image
// Promise returns when the specifid image is preloaded
// https://stackoverflow.com/a/60280239/84463
export function preloadImage(src) {
  return new Promise(r => {
    const image = new Image();
    image.onload = r;
    image.onerror = r;
    image.src = src;
  });
}

// Recursive Get
// Recursilvely get a value from a nested collection of objects.
export function rget(obj, property, delim) {
  delim = delim === undefined ? '.' : delim;
  var parts = property.split(delim);
  var key = parts.shift();
  if ((obj[key] !== undefined) && (obj[key] !== null)) {
    if (parts.length >= 1)
      return rget(obj[key], parts.join(delim), delim);
    return obj[key];
  }
  return undefined;
}

// Recursive Set
// Recursilvely set a value from a delimited string
export function rset(object, property, value) {
  var parts = property.split('.');
  var current = parts.shift();
  var pointer = object;
  while (parts.length > 0) {
    if (pointer[current] === undefined)
      pointer[current] = {};
    pointer = pointer[current];
    current = parts.shift();
  }
  pointer[current] = value;
  return object;
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

// Sleep
// JavaScript sleep function for use in async functions
// https://stackoverflow.com/a/39914235/84463
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Snackbar
// Create a new Buefy Snackbar notification with custom defaults
// https://buefy.org/documentation/snackbar
export function snackbar(message, opts) {
  var type = message.toLowerCase().includes('error') ? 'is-danger' : 'is-success';
  Snackbar.open(Object.assign({
    duration: 300000,
    message: message,
    position: 'is-top-right',
    type: type,
  }, opts));
}

// String to Bool
// Convert string to a boolean
export function strToBool(value) {
  return ['yes','y','true','t','x'].indexOf(value) >= 0;
}


// Time Ago
// Convert seconds or milliseconds to a human readable time ago string.
// https://day.js.org/docs/en/plugin/relative-time
export function timeAgo(value) {
  if (value === null || value === undefined) { return '--'; }
  if (Number.isInteger(value) && value < 99999999999) { value *= 1000; }
  return dayjs(value).fromNow();
}


// Update History
// Update the address bar history.
export function updateHistory(router, changes) {
  var query = {};
  var fullquery = Object.assign({}, router.history.current.query, changes);
  forOwn(fullquery, function(value, key) {
      if (value) { query[key] = value.toString(); }
  });
  if (!isEqual(query, router.history.current.query)) {
    router.push({query});
  }
  //query = _.pickBy(query, _.identity);  // remove falsey values
}

// USD
// Format number to USD display -$99.99 without cents.
export function usd(value, places=2) {
  var result;
  var negative = value < 0;
  value = Math.abs(value).toFixed(places);
  if (negative) { result = '-$'+ insertCommas(value); }
  else { result = '$'+ insertCommas(value); }
  if (places == 2) {
    if (result.match(/\.\d{1}$/)) { return result +'0'; }
    if (!result.match(/\./)) { return result +'.00'; }
  }
  return result;
}

// USD Int
// Format number to USD display without cents -$99
export function usdint(value) {
  return usd(value, 0);
}
