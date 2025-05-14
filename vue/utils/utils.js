// Utils.js
// Collection of utility functions

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

// Dedent
// Remove the common leading whitespace from each line in a string
export function dedent(str) {
  const lines = str.replace(/^\n/, '').split('\n')
  const indent = lines.filter(l => l.trim()).reduce((min, line) => {
    const match = line.match(/^(\s*)/)
    return match ? Math.min(min, match[1].length) : min
  }, Infinity)
  return lines.map(line => line.slice(indent)).join('\n')
}

// Escape HTML
// Escape HTML special characters
export function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, match => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;',
  }[match]))
}

// Format Date
// Format a date using various format strings:
export function formatDate(value, format) {
  format = format || 'MMM DD, YYYY'
  if (!value) { return '' }
  var date = newDate(value)
  if (isNaN(date)) { return '' }
  // Get the date components
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December']
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate() 
  const hours24 = date.getHours()
  const hours12 = hours24 % 12 || 12
  const minutes = date.getMinutes()
  const seconds = date.getSeconds()
  const ms = date.getMilliseconds()
  const dayOfWeek = date.getDay()
  const pad = (num) => String(num).padStart(2, '0')
  const getOrdinal = (n) => {
    const s = ['th', 'st', 'nd', 'rd']
    const v = n % 100
    return n + (s[(v - 20) % 10] || s[v] || s[0])
  }
  // Format map
  const formatMap = {
    YY: () => String(year).slice(-2),               // Year two digits (25)
    YYYY: () => String(year),                       // Year four digits (2025)
    Yo: () => getOrdinal(year),                     // Year, ordinal formatted (2018th)
    M: () => String(month),                         // Month number (1-12)
    MM: () => pad(month),                           // Month number with zero (01-12)
    MMM: () => monthNames[month - 1].slice(0, 3),   // Month name (Jan-Dec)
    MMMM: () => monthNames[month - 1],              // Month name (January-December)
    Mo: () => getOrdinal(month),                    // Month, ordinal formatted (1st-12th)
    D: () => String(day),                           // Day of month (1-31)
    DD: () => pad(day),                             // Day of month with zero (01-31)
    Do: () => getOrdinal(day),                      // Day of month, ordinal formatted (1st-31st)
    H: () => String(hours24),                       // Hour (0-23)
    HH: () => pad(hours24),                         // Hour with zero (01-23)
    Ho: () => getOrdinal(hours24),                  // Hour, ordinal formatted (0th-23rd)
    h: () => String(hours12),                       // 12-hour (1-12)
    hh: () => pad(hours12),                         // 12-hour with zero (01-12)
    ho: () => getOrdinal(hours12),                  // 12-Hour, ordinal formatted (1st-12th)
    m: () => String(minutes),                       // Minutes (1)
    mm: () => pad(minutes),                         // Minutes with zero (01)
    mo: () => getOrdinal(minutes),                  // Minute, ordinal formatted (0th-59th)
    s: () => String(seconds),                       // Seconds (0-59)
    ss: () => pad(seconds),                         // Seconds with zero (00-59)
    so: () => getOrdinal(seconds),                  // Second, ordinal formatted (0th-59th)
    SSS: () => String(ms).padStart(3, '0'),         // Milliseconds (000)
    A: () => hours24 >= 12 ? 'PM' : 'AM',           // Meridiem (AM/PM)
    AA: () => hours24 >= 12 ? 'P.M.' : 'A.M.',      // Meridiem with periods (A.M./P.M.)
    a: () => hours24 >= 12 ? 'pm' : 'am',           // Meridiem lowercase (am/pm)
    aa: () => hours24 >= 12 ? 'p.m.' : 'a.m.',      // Meridiem lowercase with periods (p.m./a.m.)
    d: () => String(dayOfWeek),                     // Day of week, with Sunday as 0
    dd: () => dayNames[dayOfWeek][0],               // Min name of the day of week (S-S)
    ddd: () => dayNames[dayOfWeek].slice(0, 3),     // Short name of the day of week (Sun-Sat)
    dddd: () => dayNames[dayOfWeek],                // Day of the week (Sunday-Saturday)
    z: () => date.toTimeString().slice(9, 17),      // Timezone (GMT, GMT+1)
    zz: () => date.toTimeString().slice(9, 17),     // Timezone (GMT, GMT+1)
    zzz: () => date.toTimeString().slice(9, 17),    // Timezone (GMT, GMT+1)
    zzzz: () => date.toTimeString().slice(9, 17),   // Long timezone (GMT, GMT+01:00)
  }
  // Sort the format tokens by length and replace them in the format string. This walks through each
  // character in the format string and checks all replacements from longest to shortest. If the format
  // starts with one of the replacements, we pop the relevant section of the format out of the string
  // and place the resulting formatted text into a new string. If the first character of the format
  // does not match any tokens, we simply copy that character over to the result.
  const tokens = Object.keys(formatMap).sort((a, b) => b.length - a.length)
  var result = ''
  var i = 0
  while (i < format.length) {
    var matched = false
    for (const token of tokens) {
      if (format.startsWith(token, i)) {
        result += formatMap[token]()
        i += token.length
        matched = true
        break
      }
    }
    if (!matched) { result += format[i]; i++ }
  }
  return result
}

// Get Value
// Get value of the cell in EditTable.vue
export function getItemValue(item, column, text=null) {
  text = text || column.text?.(item) || item[column.name]
  return column.format?.(text) || text
}

// Get Sign
// returns positive, zero, or negative depending on the value
export function getSign(value) {
  return value == 0 ? 'zero' : value < 0 ? 'negative' : 'positive'
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

// New Date
// Convert str to a date object. This will return the local datetime even if the
// date is in the format YYYY-MM-DD. If the date is already a date object, a new
// date of the save value is returned.
export function newDate(value) {
  if (value == null || value == undefined) { return null }
  if (value instanceof Date) { return new Date(value) }
  if (typeof value == 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-').map(Number)
    return new Date(year, month-1, day)
  } else {
    return new Date(value)
  }
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

// Stringify
// A better pretty printer for JSON string.
// Options: {indent:2, maxlen:80, json:JSON, replacer:null}
// https://github.com/lydell/json-stringify-pretty-compact
export function stringify(passedobj, opts={}) {
  opts = {indent:2, maxlen:80, replacer:null, json:JSON, ...opts}
  const strorchar = /("(?:[^\\"]|\\.)*")|[:,]/g
  const indent = '    '.slice(0, opts.indent)
  const maxlen = indent == '' ? Infinity : opts.maxlen == undefined ? 80 : opts.maxlen
  var {replacer} = opts

  return (function _stringify(obj, curindent, reserved) {
    if (obj && typeof obj.toJSON === 'function') { obj = obj.toJSON() }
    const string = opts.json.stringify(obj, replacer)
    if (string === undefined) { return string }
    const length = maxlen - curindent.length - reserved
    if (string.length <= length) {
      const pretty = string.replace(strorchar, function(match, strliteral) {
        return strliteral || `${match} `
      })
      if (pretty.length <= length) { return pretty }
    }
    if (replacer !== null) {
      obj = opts.json.parse(string)
      replacer = undefined
    }
    if (typeof obj == 'object' && obj !== null) {
      const nextindent = curindent + indent
      const items = []
      var start, end
      if (Array.isArray(obj)) {
        start = '[', end = ']'
        const {length} = obj
        for (var i=0; i < length; i++) {
          items.push(_stringify(obj[i], nextindent, i == length-1 ? 0:1) || 'null')
        }
      } else {
        start = '{', end='}'
        var keys = Object.keys(obj)
        const {length} = keys
        for (let index=0; index < length; index++) {
          const key = keys[index]
          const keypart = `${opts.json.stringify(key)}: `
          const value = _stringify(obj[key], nextindent, keypart.length + (index == length-1 ? 0:1))
          if (value !== undefined) { items.push(keypart + value) }
        }
      }
      if (items.length > 0) {
        return [start, indent + items.join(`,\n${nextindent}`), end].join(`\n${curindent}`)
      }
    }
    return string
  })(passedobj, '', 0)
}

// Time Ago
// Convert seconds or milliseconds to a human readable time ago string.
export function timeAgo(value, shorten) {
  shorten = shorten === undefined ? false : shorten
  if (value === null || value === undefined) { return 'Never' }
  if (Number.isInteger(value) && value < 99999999999) { value *= 1000 }
  // Calculate difference in seconds, minutes, hours, days, weeks, and months
  const now = Date.now()
  const diff = now - value
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60) 
  const days = Math.floor(hours / 24)
  const weeks = Math.floor(days / 7)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)
  // Build the return string
  var result
  if (years > 0) { result = years === 1 ? '1 year ago' : `${years} years ago` }
  else if (months > 0) { result = months === 1 ? '1 month ago' : `${months} months ago` }
  else if (weeks > 0) { result = weeks === 1 ? '1 week ago' : `${weeks} weeks ago` }
  else if (days > 0) { result = days === 1 ? '1 day ago' : `${days} days ago` }
  else if (hours > 0) { result = hours === 1 ? '1 hour ago' : `${hours} hours ago` }
  else if (minutes > 0) { result = minutes === 1 ? '1 minute ago' : `${minutes} minutes ago` }
  else { result = seconds <= 1 ? '1 second ago' : `${seconds} seconds ago` }
  // Shorten the return string if requested
  if (shorten && !result.includes('just')) {
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

// Title
// Titleize the specified string
export function title(str) {
  str = str.replace(/_/g, ' ').split(' ')
  str = str.map(w => w.length > 0 ? w[0].toUpperCase() + w.substring(1) : w)
  return str.join(' ')
}

// Template
// Replace {{context.key}} with the value from the context object
export function tmpl(str, context) {
  return str.replace(/{{\s*([\w.$]+)\s*}}/g, (_, path) => {
    const value = rget(context, path)
    return value != null ? escapeHtml(value) : ''
  })
}

// USD
// Format number to USD display -$99.99 with cents.
export function usd(value, places=2, symbol='$', sigdigs=null) {
  const absval = Math.abs(value || 0)
  if (sigdigs && absval >= 10000) {
    const units = [{size:1e6, unit:'M'}, {size:1e3, unit:'K'}]
    for (var {size,unit} of units) {
      if (absval >= size) {
        let n = (absval / size).toPrecision(sigdigs)
        var [intPart, decPart] = n.split('.')
        if (decPart !== undefined) {
          n = intPart + '.' + decPart.padEnd(sigdigs - intPart.length, '0')
          n = n.replace(/(\.\d*?[1-9])0+$/, '$1')
        }
        return `${value < 0 ? '-' : ''}${symbol}${n}${unit}`
      }
    }
  }
  places = places == 0 && value < 1 && value > -1 && value != 0 ? 2 : places
  let result = `${symbol}${intComma(absval.toFixed(places))}`
  if (value < 0) result = `-${result}`
  if (places == 2) {
    if (result.match(/\.\d{1}$/)) return result + '0'
    if (!result.includes('.')) return result + '.00'
  }
  return result
}


// USD Int
// Format number to USD display without cents -$99
export function usdint(value, opts={}) {
  opts = Object.assign({}, opts, {places:0})
  return usd(value, opts)
}
