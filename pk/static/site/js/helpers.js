// Encoding: UTF-8
// Collection of handlebar helpers from the following git
// repo formatted for use on the web.
// SOURCE: https://github.com/assemble/handlebars-helpers
// LICENSE: https://github.com/assemble/handlebars-helpers/blob/master/LICENSE-MIT
'use strict';


// -----------------------------
// General Utils
// https://github.com/assemble/handlebars-helpers/blob/master/lib/utils/utils.js
// https://github.com/assemble/handlebars-helpers/blob/master/lib/utils/dates.js
// -----------------------------
var helperutils = {
  date_formats: /%(a|A|b|B|c|C|d|D|e|F|h|H|I|j|k|l|L|m|M|n|p|P|q|r|R|s|S|t|T|u|U|v|V|W|w|x|X|y|Y|z)/g,
  dates_abbreviatedWeekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat'],
  dates_fullWeekdays: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  dates_abbreviatedMonths: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  dates_fullMonths: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
  
  isFunction: function(obj) {
    return typeof obj === 'function';
  },
   
  isUndefined: function(value) {
    return value === undefined;
  },
  
  result: function(value) {
    return this.isFunction(value) ? value() : value;
  },
  
  safeString: function(str) {
    return new Handlebars.SafeString(str);
  },
  
  toString: function(val) {
    return val === null ? '' : val.toString();
  },
  
  padNumber: function(num, count, padCharacter) {
    if (typeof padCharacter === 'undefined') {
      padCharacter = '0';
    }
    var lenDiff = count - String(num).length;
    var padding = '';
    if (lenDiff > 0) {
      while (lenDiff--) {
        padding += padCharacter;
      }
    }
    return padding + num;
  },

  dayOfYear: function(date) {
    var oneJan = new Date(date.getFullYear(), 0, 1);
    return Math.ceil((date - oneJan) / 86400000);
  },

  weekOfYear: function(date) {
    var oneJan = new Date(date.getFullYear(), 0, 1);
    return Math.ceil((((date - oneJan) / 86400000) + oneJan.getDay() + 1) / 7);
  },

  isoWeekOfYear: function(date) {
    var target = new Date(date.valueOf());
    var dayNr = (date.getDay() + 6) % 7;
    target.setDate(target.getDate() - dayNr + 3);
    var jan4 = new Date(target.getFullYear(), 0, 4);
    var dayDiff = (target - jan4) / 86400000;
    return 1 + Math.ceil(dayDiff / 7);
  },

  tweleveHour: function(date) {
    if (date.getHours() == 0) { return 12; }
    return date.getHours() > 12 ? date.getHours() - 12 : date.getHours();
  },

  timeZoneOffset: function(date) {
    var hoursDiff = -date.getTimezoneOffset() / 60;
    var result = this.padNumber(Math.abs(hoursDiff), 4);
    return (hoursDiff > 0 ? '+' : '-') + result;
  },

  format: function(date, format) {
    var self = this;
    var match = null;
    return format.replace(this.date_formats, function(m, p) {
      switch (p) {
        case 'a': return self.dates_abbreviatedWeekdays[date.getDay()];
        case 'A': return self.dates_fullWeekdays[date.getDay()];
        case 'b': return self.dates_abbreviatedMonths[date.getMonth()];
        case 'B': return self.dates_fullMonths[date.getMonth()];
        case 'c': return date.toLocaleString();
        case 'C': return Math.round(date.getFullYear() / 100);
        case 'd': return self.padNumber(date.getDate(), 2);
        case 'D': return self.format(date, '%m/%d/%y');
        case 'e': return self.padNumber(date.getDate(), 2, ' ');
        case 'F': return self.format(date, '%Y-%m-%d');
        case 'h': return self.format(date, '%b');
        case 'H': return self.padNumber(date.getHours(), 2);
        case 'I': return self.padNumber(self.tweleveHour(date), 2);
        case 'j': return self.padNumber(self.dayOfYear(date), 3);
        case 'k': return self.padNumber(date.getHours(), 2, ' ');
        case 'l': return self.padNumber(self.tweleveHour(date), 2, ' ');
        case 'L': return self.padNumber(date.getMilliseconds(), 3);
        case 'm': return self.padNumber(date.getMonth() + 1, 2);
        case 'M': return self.padNumber(date.getMinutes(), 2);
        case 'n': return '\n';
        case 'p': return date.getHours() > 11 ? 'PM' : 'AM';
        case 'q': return date.getHours() > 11 ? 'pm' : 'am';
        case 'P': return self.format(date, '%p').toLowerCase();
        case 'r': return self.format(date, '%I:%M:%S %p');
        case 'R': return self.format(date, '%H:%M');
        case 's': return date.getTime() / 1000;
        case 'S': return self.padNumber(date.getSeconds(), 2);
        case 't': return '\t';
        case 'T': return self.format(date, '%H:%M:%S');
        case 'u': return date.getDay() === 0 ? 7 : date.getDay();
        case 'U': return self.padNumber(self.weekOfYear(date), 2);
        case 'v': return self.format(date, '%e-%b-%Y');
        case 'V': return self.padNumber(self.isoWeekOfYear(date), 2);
        case 'W': return self.padNumber(self.weekOfYear(date), 2);
        case 'w': return self.padNumber(date.getDay(), 2);
        case 'x': return date.toLocaleDateString();
        case 'X': return date.toLocaleTimeString();
        case 'y': return String(date.getFullYear()).substring(2);
        case 'Y': return date.getFullYear();
        case 'z': return self.timeZoneOffset(date);
        default: return match;
      }
    });
  },
};


// -----------------------------
// Collection Helpers
// https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-collections.js
// -----------------------------

var helpers = {

  _register: function() {
    for (var helper in this) {
      if (helper.charAt(0) != '_') {
        Handlebars.registerHelper(helper, this[helper]);
      }
    }
  },

  any: function(array, options) {
    if (array.length > 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  /**
   * Returns all of the items in the collection after the specified count.
   * @param  {Array}  array Collection
   * @param  {Number} count Number of items to exclude
   * @return {Array}        Array excluding the number of items specified
   */
  after: function(array, count) {
    return array.slice(count);
  },

  /**
   * Use all of the items in the collection after the specified count
   * inside a block.
   */
  withAfter: function(array, count, options) {
    array = array.slice(count);
    var result = '';
    for (var item in array) {
      result += options.fn(array[item]);
    }
    return result;
  },

  /**
   * Converts a string such as "foo, bar, baz" to an ES Array of strings.
   * @credit: http://bit.ly/1840DsB
   */
  arrayify: function(str) {
    return str.split(',').map(function(tag) {
      return "\"" + tag + "\"";
    });
  },

  /**
   * Returns all of the items in the collection before the specified
   * count. Opposite of {{after}}.
   */
  before: function(array, count) {
    return array.slice(0, -count);
  },

  /**
   * Use all of the items in the collection before the specified count
   * inside a block. Opposite of {{withAfter}}
   */
  withBefore: function(array, count, options) {
    array = array.slice(0, -count);
    var result = '';
    for (var item in array) {
      result += options.fn(array[item]);
    }
    return result;
  },

  /**
   * Returns the first item in a collection.
   */
  first: function(array, count) {
    if (helperutils.isUndefined(count)) {
      return array[0];
    } else {
      return array.slice(0, count);
    }
  },

  /**
   * Use the first item in a collection inside a block.
   */
  withFirst: function(array, count, options) {
    if (!helperutils.isUndefined(array)) {
      array = helperutils.result(array);
      if (!helperutils.isUndefined(count)) {
        count = parseFloat(helperutils.result(count));
      }
      if (helperutils.isUndefined(count)) {
        options = count;
        return options.fn(array[0]);
      } else {
        array = array.slice(0, count);
        var result = '';
        for (var item in array) {
          result += options.fn(array[item]);
        }
        return result;
      }
    } else {
      return console.error('{{withFirst}} takes at least one argument (array).');
    }
  },

  /**
   * Returns the last item in a collection. Opposite of `first`.
   */
  last: function(array, count) {
    if (helperutils.isUndefined(count)) {
      return array[array.length - 1];
    } else {
      return array.slice(-count);
    }
  },

  /**
   * Use the last item in a collection inside a block.
   * Opposite of {{withFirst}}.
   */
  withLast: function(array, count, options) {
    if (helperutils.isUndefined(count)) {
      options = count;
      return options.fn(array[array.length - 1]);
    } else {
      array = array.slice(-count);
      var result = '';
      for (var item in array) {
        result += options.fn(array[item]);
      }
      return result;
    }
  },

  /**
   * Joins all elements of a collection into a string
   * using a separator if specified.
   */
  join: function(array, separator) {
    return array.join(helperutils.isUndefined(separator) ? ' ' : separator);
  },

  /**
   * Handlebars "joinAny" block helper that supports
   * arrays of objects or strings. implementation found here:
   * https://github.com/wycats/handlebars.js/issues/133
   *
   * If "delimiter" is not speficified, then it defaults to ",".
   * You can use "start", and "end" to do a "slice" of the array.
   * @example:
   *   Use with objects:
   *   {{#join people delimiter=" and "}}{{name}}, {{age}}{{/join}}
   * @example:
   *   Use with arrays:
   *   {{join jobs delimiter=", " start="1" end="2"}}
   *
   */
  joinAny: function(items, block) {
    var delimiter = block.hash.delimiter || ",";
    var start = block.hash.start || 0;
    var len = (items ? items.length : 0);
    var end = block.hash.end || len;
    var out = '';
    if (end > len) {
      end = len;
    }
    if ('function' === typeof block) {
      var i = start;
      while (i < end) {
        if (i > start) {
          out += delimiter;
        }
        if ('string' === typeof items[i]) {
          out += items[i];
        } else {
          out += block(items[i]);
        }
        i++;
      }
      return out;
    } else {
      return [].concat(items).slice(start, end).join(delimiter);
    }
  },

  sort: function(array, field) {
    if (helperutils.isUndefined(field)) {
      return array.sort();
    } else {
      return array.sort(function(a, b) {
        return a[field] > b[field];
      });
    }
  },

  withSort: function(array, field, options) {
    array = _.cloneDeep(array);
    var getDescendantProp = function(obj, desc) {
      var arr = desc.split('.');
      while (arr.length && (obj = obj[arr.shift()])) {
        continue;
      }
      return obj;
    };
    var result = '';
    var item;
    var i;
    var len;
    if (helperutils.isUndefined(field)) {
      options = field;
      array = array.sort();
      if (options.hash && options.hash.dir === 'desc') {
        array = array.reverse();
      }
      for (i = 0, len = array.length; i < len; i++) {
        item = array[i];
        result += options.fn(item);
      }
    } else {
      array = array.sort(function(a, b) {
        var aProp = getDescendantProp(a, field);
        var bProp = getDescendantProp(b, field);
        if (aProp > bProp) {
          return 1;
        } else {
          if (aProp < bProp) {
            return -1;
          }
        }
        return 0;
      });
      if (options.hash && options.hash.dir === 'desc') {
        array = array.reverse();
      }
      for (item in array) {
        result += options.fn(array[item]);
      }
    }
    return result;
  },

  length: function(array) {
    return (!array) ? 0 : array.length;
  },

  lengthEqual: function(array, length, options) {
    if (array.length === length) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  empty: function(array, options) {
    if (array.length <= 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  inArray: function(array, value, options) {
    var _indexOf = require('../utils/lib/indexOf');
    if (_indexOf.call(array, value) >= 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  filter: function(array, value, options) {
    var data = void 0;
    var content = '';
    var results = [];
    if (options.data) {
      data = Handlebars.createFrame(options.data);
    }
    // filtering on a specific property
    if (options.hash && options.hash.property) {
      var search = {};
      search[options.hash.property] = value;
      results = _.filter(array, search);
    } else {
      // filtering on a string value
      results = _.filter(array, function(v, k) {
        return value === v;
      });
    }
    if (results && results.length > 0) {
      for(var i=0; i < results.length; i++){
        content += options.fn(results[i], {data: data});
      }
    } else {
      content = options.inverse(this);
    }
    return content;
  },

  /**
   * Similar to {{#each}} helper, but treats array-like objects
   * as arrays (e.g. objects with a `.length` property that
   * is a number) rather than objects. This lets us iterate
   * over our collections items.
   */
  iterate: function(context, options) {
    var fn = options.fn;
    var inverse = options.inverse;
    var i = 0;
    var ret = "";
    var data = void 0;
    if (options.data) {
      data = Handlebars.createFrame(options.data);
    }
    if (context && typeof context === 'object') {
      if (typeof context.length === 'number') {
        var j = context.length;
        while (i < j) {
          if (data) {data.index = i;}
          ret = ret + fn(context[i], {data: data});
          i++;
        }
      } else {
        for (var key in context) {
          if (context.hasOwnProperty(key)) {
            if (data) {data.key = key;}
            ret = ret + fn(context[key], {data: data});
            i++;
          }
        }
      }
    }
    if (i === 0) {ret = inverse(this);}
    return ret;
  },

  /**
   * Credit: http://bit.ly/14HLaDR
   * @example:
   *   var accounts = [
   *     {'name': 'John', 'email': 'john@example.com'},
   *     {'name': 'Malcolm', 'email': 'malcolm@example.com'},
   *     {'name': 'David', 'email': 'david@example.com'}
   *   ];
   *
   *   {{#forEach accounts}}
   *     <a href="mailto:{{ email }}" title="Send an email to {{ name }}">
   *       {{ name }}
   *     </a>{{#unless isLast}}, {{/unless}}
   *   {{/forEach}}
   */
  forEach: function(array, fn) {
    var total = array.length;
    var buffer = "";
    // Better performance: http://jsperf.com/for-vs-forEach/2
    var i = 0;
    var j = total;
    while (i < j) {
      // stick an index property onto the item, starting
      // with 1, may make configurable later
      var item = array[i];
      item.index = i + 1;
      item._total = total;
      item.isFirst = i === 0;
      item.isLast = i === (total - 1);
      // show the inside of the block
      buffer += fn.fn(item);
      i++;
    }
    // return the finished buffer
    return buffer;
  },

  /**
   * Handlebars block helper to enumerate
   * the properties in an object
   */
  eachProperty: function(context, options) {
    var content = (function() {
      var results = [];
      for (var key in context) {
        var value = context[key];
        results.push(options.fn({
          key: key,
          value: value
        }));
      }
      return results;
    })();
    return content.join('');
  },

  /**
   * {{#eachIndex collection}}
   *   {{item}} is {{index}}
   * {{/eachIndex}}
   */
  eachIndex: function(array, options) {
    var i;
    var len;
    var result = '';
    var index;
    for (index = i = 0, len = array.length; i < len; index = ++i) {
      var value = array[index];
      result += options.fn({
        item: value,
        index: index
      });
    }
    return result;
  },

  // -----------------------------
  // Comparison Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-comparisons.js
  // -----------------------------

  contains: function(str, pattern, options) {
    if (str.indexOf(pattern) !== -1) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  and: function(a, b, options) {
    if (a && b) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  icontains: function(str, pattern, options) {
    str = str.toLowerCase();
    pattern = pattern.toLowerCase();
    if (str.indexOf(pattern) !== -1) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  is: function(value, test, options) {
    if (value === test) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  isnt: function(value, test, options) {
    if (value !== test) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  or: function(a, b, options) {
    if (a || b) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  if_nth: function(nr, v, options) {
    v = v+1;
    if (v % nr === 0) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  if_eq: function(value, other, options) {
    if (value === other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_eq: function(value, other, options) {
    if (value === other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_gt: function(value, other, options) {
    if (value > other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_gt: function(value, other, options) {
    if (value > other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_lt: function(value, other, options) {
    if (value < other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_lt: function(value, other, options) {
    if (value < other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_gte: function(value, other, options) {
    if (value >= other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_gte: function(value, other, options) {
    if (value >= other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  if_lte: function(value, other, options) {
    if (value <= other) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  unless_lte: function(value, other, options) {
    if (value <= other) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * Similar to {{#if}} block helper but accepts multiple arguments.
   * @author: Dan Harper <http://github.com/danharper>
   * @example: {{ifAny this that}}
   */
  ifAny: function() {
    var argLength = arguments.length - 1;
    var content = arguments[argLength];
    var success = true;
    var i = 0;
    while (i < argLength) {
      if (!arguments[i]) {
        success = false;
        break;
      }
      i += 1;
    }
    if (success) {
      return content.fn(this);
    }
    return content.inverse(this);
  },

  /**
   * Determine whether or not the @index is an even number or not
   * @author: Stack Overflow Answer <http://stackoverflow.com/questions/18976274/odd-and-even-number-comparison-helper-for-handlebars/18993156#18993156>
   * @author: Michael Sheedy <http://github.com/sheedy> (found code and added to repo)
   * @example: {{ifEven @index}}
   */
  ifEven: function(conditional, options) {
    if ((conditional % 2) === 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  // -----------------------------
  // Date Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-dates.js
  // -----------------------------

  /**
   * Port of formatDate-js library (http://bit.ly/18eo2xw)
   */
  formatDate: function(datestr, format) {
    var date = moment(datestr).toDate();
    return helperutils.format(date, format);
  },

  now: function(format) {
    console.log('--- 1 ---');
    console.log(format)
    var date = new Date();
    if (helperutils.isUndefined(format)) {
      return date;
    }
    console.log('--- 2 ---');
    return helperutils.format(date, format);
  },

  /**
   * Modified version of http://bit.ly/18WwJYf
   */
  timeAgo: function(date) {
    date = new Date(date);
    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = Math.floor(seconds / 31536000);
    if (interval > 1) { return "" + interval + " years ago"; }
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) { return "" + interval + " months ago"; }
    interval = Math.floor(seconds / 86400);
    if (interval > 1) { return "" + interval + " days ago"; }
    interval = Math.floor(seconds / 3600);
    if (interval > 1) { return "" + interval + " hours ago"; }
    interval = Math.floor(seconds / 60);
    if (interval > 1) { return "" + interval + " minutes ago"; }
    if (Math.floor(seconds) === 0) {
      return 'Just now';
    } else {
      return Math.floor(seconds) + ' seconds ago';
    }
  },
  
  // -----------------------------
  // Logging Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-logging.js
  // -----------------------------
  
  log: function(value) {
    return console.log(value);
  },
  
  // -----------------------------
  // Math Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-math.js
  // -----------------------------
  
  abs: function(value) {
    return Math.abs(value);
  },

  add: function(value, addition) {
    return value + addition;
  },

  subtract: function(value, substraction) {
    return value - substraction;
  },

  divide: function(value, divisor) {
    return value / divisor;
  },

  multiply: function(value, multiplier) {
    return value * multiplier;
  },

  floor: function(value) {
    return Math.floor(value);
  },

  ceil: function(value) {
    return Math.ceil(value);
  },

  round: function(value) {
    return Math.round(value);
  },

  sum: function() {
    var args = _.flatten(arguments);
    var sum = 0;
    var i = args.length - 1;
    while (i--) {
      sum +=  _.parseInt(args[i]) || 0;
    }
    return Number(sum);
  },
  
  // -----------------------------
  // Miscellaneous Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-miscellaneous.js
  // -----------------------------
  
  default: function(value, defaultValue) {
    return value !== null ? value : defaultValue;
  },

  /**
   * http://handlebarsjs.com/block_helpers.html
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   */
  noop: function(options) {
    return options.fn(this);
  },

  /**
   * Build context from the attributes hash
   * @author Vladimir Kuznetsov <https://github.com/mistakster>
   */
  withHash: function(options) {
    return options.fn(options.hash || {});
  },
  
  // -----------------------------
  // Number Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-numbers.js
  // -----------------------------
  
  /**
   * Add commas to numbers
   */
  addCommas: function(number) {
    return number.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
  },

  /**
   * Round to the nearest int value and add commas to numbers
   */
  amountInt: function(amount) {
    return pk.utils.to_amount_int(amount);
  },

  amountIntAbs: function(amount) {
    return pk.utils.to_amount_int(Math.abs(amount));
  },

  /**
   * Round to the nearest 2 decimals and add commas to numbers
   */
  amountFloat: function(amount) {
    return pk.utils.to_amount_float(amount);
  },

 /**
  * Output a formatted phone number (800) 555-1212
  * @author: http://bit.ly/QlPmPr
  */
  formatPhoneNumber: function(num) {
    num = num.toString();
    return "(" + num.substr(0, 3) + ") " + num.substr(3, 3) + "-" + num.substr(6, 4);
  },

  /**
   * Generate a random number between two values
   * @author Tim Douglas <https://github.com/timdouglas>
   */
  random: function(min, max) {
    return _.random(min, max);
  },

  /**
   * Abbreviate numbers
   */
  toAbbr: function(number, digits) {
    if (helperutils.isUndefined(digits)) {
      digits = 2;
    }
    // @default: 2 decimal places => 100, 3 => 1000, etc.
    digits = Math.pow(10, digits);
    var abbr = ["k", "m", "b", "t"];
    var i = abbr.length - 1;
    while (i >= 0) {
      var size = Math.pow(10, (i + 1) * 3);
      if (size <= number) {
        number = Math.round(number * digits / size) / digits;
        // Special case where we round up to the next abbreviation
        if ((number === 1000) && (i < abbr.length - 1)) {
          number = 1;
          i++;
        }
        number += abbr[i];
        break;
      }
      i--;
    }
    return number;
  },

  toExponential: function(number, fractions) {
    if (helperutils.isUndefined(fractions)) {
      fractions = 0;
    }
    return number.toExponential(fractions);
  },

  toFixed: function(number, digits) {
    if (helperutils.isUndefined(digits)) {
      digits = 0;
    }
    return number.toFixed(digits);
  },

  toFloat: function(number) {
    return parseFloat(number);
  },

  toInt: function(number) {
    return parseInt(number, 10);
  },

  toPrecision: function(number, precision) {
    if (helperutils.isUndefined(precision)) {
      precision = 1;
    }
    return number.toPrecision(precision);
  },
  
  // -----------------------------
  // String Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-strings.js
  // -----------------------------
  
  /**
   * Capitalize first word in a sentence
   */
  capitalizeFirst: function(str) {
    if (str && typeof str === "string") {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
  },

  /**
   * Capitalize each word in a sentence
   */
  capitalizeEach: function(str) {
    if (str && typeof str === "string") {
      return str.replace(/\w\S*/g, function(word) {
        return word.charAt(0).toUpperCase() + word.substr(1);
      });
    }
  },

  /**
   * Center a string using non-breaking spaces
   */
  center: function(str, spaces) {
    if (str && typeof str === "string") {
      var space = '';
      var i = 0;
      while (i < spaces) {
        space += '&nbsp;';
        i++;
      }
      return "" + space + str + space;
    }
  },

  /**
   * Replace periods in string with hyphens.
   */
  dashify: function(str) {
    if (str && typeof str === "string") {
      return str.split(".").join("-");
    }
  },

  /**
   * Replace spaces in string with hyphens.
   */
  hyphenate: function(str) {
    if (str && typeof str === "string") {
      return str.split(" ").join("-");
    }
  },

  /**
   * Make all letters in the string lowercase
   */
  lowercase: function(str) {
    if (str && typeof str === "string") {
      return str.toLowerCase();
    }
  },
  
  /**
   * Replace spaces in string with pluses.
   * @author: Stephen Way <https://github.com/stephenway>
   */
  plusify: function(str) {
    if (str && typeof str === "string") {
      return str.split(" ").join("+");
    }
  },

  /**
   * Output a Handlebars safeString
   */
  safeString: function(str) {
    if (str && typeof str === "string") {
      return new helperutils.safeString(str);
    }
  },

  /**
   * Sentence case
   */
  sentence: function(str) {
    if (str && typeof str === "string") {
      return str.replace(/((?:\S[^\.\?\!]*)[\.\?\!]*)/g, function(txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
    }
  },

  /**
   * Title case. "This is Title Case"
   */
  titleize: function(str) {
    if (str && typeof str === "string") {
      var title = str.replace(/[ \-_]+/g, ' ');
      var words = title.match(/\w+/g);
      var capitalize = function(word) {
        return word.charAt(0).toUpperCase() + word.slice(1);
      };
      return ((function() {
        var i, len, results;
        results = [];
        for (i = 0, len = words.length; i < len; i++) {
          var word = words[i];
          results.push(capitalize(word));
        }
        return results;
      })()).join(' ');
    }
  },

  uppercase: function(options) {
    if (options && typeof options === "string") {
      return options.toUpperCase();
    } else if (options && typeof options === "object") {
      return options.fn(this).toUpperCase();
    }
  },

  reverse: function(str) {
    if (str && typeof str === "string") {
      return str.split('').reverse().join('');
    }
  },

  /**
   * Return the number of occurrances of a string, within a string
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {String} str       The haystack
   * @param  {String} substring The needle
   * @return {Number}           The number of times the needle is found in the haystack.
   */
  count: function(str, substring) {
    if (str && typeof str === "string") {
      var n = 0;
      var pos = 0;
      var l = substring.length;
      while (true) {
        pos = str.indexOf(substring, pos);
        if (pos > -1) {
          n++;
          pos += l;
        } else {
          break;
        }
      }
      return n;
    }
  },

  /**
   * Replace occurrences of string "A" with string "B"
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   */
  replace: function(str, a, b) {
    if (str && typeof str === "string") {
      return str.split(a).join(b);
    }
  },

  /**
   * Truncate the input string and removes all HTML tags
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {String} str      The input string.
   * @param  {Number} limit    The number of characters to limit the string.
   * @param  {String} append   The string to append if charaters are omitted.
   * @return {String}          The truncated string.
   */
  ellipsis: function(str, limit, append) {
    if (helperutils.isUndefined(append)) {
      append = '';
    }
    var sanitized = str.replace(/(<([^>]+)>)/g, '');
    if (sanitized.length > limit) {
      return sanitized.substr(0, limit - append.length) + append;
    }
    return sanitized;
  },

  /**
   * Truncates a string given a specified `length`,
   * providing a custom string to denote an `omission`.
   */
  truncate: function(str, limit, omission) {
    if (helperutils.isUndefined(omission)) {
      omission = '';
    }
    if (str.length > limit) {
      return str.substring(0, limit - omission.length) + omission;
    }
    return str;
  },

  /**
   * Tests whether a string begins with the given prefix.
   * Behaves sensibly if the string is null.
   * @author: Dan Fox <http://github.com/iamdanfox>
   *
   * @example:
   *   {{#startsWith "Goodbye" "Hello, world!"}}
   *     Whoops
   *   {{else}}
   *     Bro, do you even hello world?
   *   {{/startsWith}}
   */
  startsWith: function(prefix, str, options) {
    if ((str !== null ? str.indexOf(prefix) : void 0) === 0) {
      return options.fn(this);
    }
    return options.inverse(this);
  },
  
  // -----------------------------
  // URL Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-url.js
  // -----------------------------
  
  stripQuerystring: function(url) {
    return url.split("?")[0];
  },

  /**
   * Encodes a Uniform Resource Identifier (URI) component
   * by replacing each instance of certain characters by
   * one, two, three, or four escape sequences representing
   * the UTF-8 encoding of the character.
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   */
  encodeURI: function(uri) {
    return encodeURIComponent(uri);
  },

  /**
   * Decodes a Uniform Resource Identifier (URI) component
   * previously created by encodeURIComponent or by a
   * similar routine.
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   */
  decodeURI: function(encodedURI) {
    return decodeURIComponent(encodedURI);
  },

  /**
   * Return yes or no based on the test
   */
  yesNo: function(test, yes, no) {
    return test ? yes : no;
  },

};
