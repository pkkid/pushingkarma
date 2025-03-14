import {useDateFormat, useTimeAgo} from '@vueuse/core'


// Set apibase URL to port 8000 if running in development mode.
// This is the port that the Django runserver uses.
export const apibase = process.env.NODE_ENV === 'development' ?
  `http://${window.location.hostname}:8000/api/` :
  `http://${window.location.hostname}/api/`

// Animate
// animate the specified element
export function animate(elem, animation, duration) {
  elem.classList.add(animation)
  setTimeout(() => {
    elem.classList.remove(animation)
  }, duration)
}

// Cancel
// Cancel the specified request
export function cancel(request) {
  if (request) { request.cancel() }
}

// Copy To Clipboard
// If event is passed, try to animate the element
export function copyText(text, event) {
  const clipboard = window.clipboardData || navigator.clipboard
  clipboard.writeText(text)
  if (event) {
    var button = event.target.closest('.p-button')
    button.style.transition = 'none'
    button.style.backgroundColor = '#999'
    button.offsetHeight
    button.style.transition = 'background-color 0.6s ease'
    button.style.backgroundColor = ''
  }
}

// Debounce
// Useful to debounce ajax calls
export function debounce(func, wait=500) {
  let timeout
  return function(...args) {
    const context = this
    clearTimeout(timeout)
    timeout = setTimeout(() => func.apply(context, args), wait)
  }
}

// Format Date
// https://vueuse.org/shared/useDateFormat/
export function formatDate(value, format) {
  format = format || 'MMM DD, YYYY'
  return useDateFormat(value, format).value
}

// Insert Commas
// Add commas to the specified number.
export function intComma(value) {
  if (!value) { return 0 }
  var parts = value.toString().split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return parts.join('.')
}

// Int
// Wrapper around parseInt
export function int(value) {
  return parseInt(value, 10)
}

// Pop
// Remove and return an item from an object
export function pop(obj, key) {
  if (Object.prototype.hasOwnProperty.call(obj, key)) {
    const value = obj[key]
    delete obj[key]
    return value
  }
  return null
}

// Round
// Round the number to the specified decimal places
export function round(value, decimals) {
  return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals)
}

// Recursive Get
// Recursilvely get a value from a nested collection of objects.
export function rget(obj, property, delim) {
  delim = delim === undefined ? '.' : delim
  var parts = property.split(delim)
  var key = parts.shift()
  if ((obj[key] !== undefined) && (obj[key] !== null)) {
    if (parts.length >= 1)
      return rget(obj[key], parts.join(delim), delim)
    return obj[key]
  }
  return undefined
}

// Recursive Set
// Recursilvely set a value from a delimited string
export function rset(object, property, value) {
  var parts = property.split('.')
  var current = parts.shift()
  var pointer = object
  while (parts.length > 0) {
    if (pointer[current] === undefined) {
      pointer[current] = {}
    }
    pointer = pointer[current]
    current = parts.shift()
  }
  pointer[current] = value
  return object
}

// Set Nav Position
// set the main site nav position to top or left.
export function setNavPosition(pos) {
  document.body.classList.remove(`leftnav`)
  document.body.classList.remove(`topnav`)
  document.body.classList.add(`${pos}nav`)
}

// Slug
// Removes all special characters and replaces spaces with hyphens.
export function slug(value) {
  if (!value) { return '' }
  return value.toString().toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^\w\s-]+/g, '').trim()
    .replace(/[\s]+/g, '-')
}

// Sort
// Generic Sort for arrays or Object Keys
export function sort(value) {
  if (Array.isArray(value)) {
    return value.sort()
  } else if (typeof value === 'object' && value !== null) {
    return Object.keys(value).sort().reduce(function(obj, key) {
      obj[key] = value[key]
      return obj
    }, {})
  }
}

// Time Ago
// Convert seconds or milliseconds to a human readable time ago string.
// https://day.js.org/docs/en/plugin/relative-time
export function timeAgo(value, shorten) {
  shorten = shorten === undefined ? false : shorten
  if (value === null || value === undefined) { return 'Never' }
  if (Number.isInteger(value) && value < 99999999999) { value *= 1000 }
  var result = useTimeAgo(value).value
  if (shorten && !result.includes('last')) {
    result = result.replace(' years', 'y').replace(' year', 'y')
    result = result.replace(' months', 'mo').replace(' month', 'm')
    result = result.replace(' weeks', 'w').replace(' week', 'w')
    result = result.replace(' days', 'd').replace(' day', 'd')
    result = result.replace(' hours', 'hrs').replace(' hour', 'hr')
    result = result.replace(' minutes', 'min').replace(' minute', 'min')
    result = result.replace(' seconds', 's').replace(' second', 's')
  }
  return result
}
