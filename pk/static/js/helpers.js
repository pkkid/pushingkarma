/*----------------------------------------------------------
 * Collection of handlebar helpers from the following git
 * repo formatted for use on the web.
 * SOURCE: https://github.com/assemble/handlebars-helpers
 * LICENSE: https://github.com/assemble/handlebars-helpers/blob/master/LICENSE-MIT
 *------------------------------------------------------- */
'use strict';

var helperutils = {
  
  // -----------------------------
  // General Utils
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/utils/utils.js
  // -----------------------------
  
  isFunction: function (obj) {
    return typeof obj === 'function';
  },
   
  isUndefined: function (value) {
    return typeof value === 'undefined' || this.toString.call(value) === '[object Function]' || (value.hash !== null);
  },
  
  result: function(value) {
    if (this.isFunction(value)) {
      return value();
    } else {
      return value;
    }
  },
  
  safeString: function (str) {
    return new Handlebars.SafeString(str);
  },
  
  toString: function (val) {
    if (val === null) {
      return '';
    } else {
      return val.toString();
    }
  },
  
  // -----------------------------
  // Date Utils
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/utils/dates.js
  // -----------------------------
  
  date_formats: /%(a|A|b|B|c|C|d|D|e|F|h|H|I|j|k|l|L|m|M|n|p|P|r|R|s|S|t|T|u|U|v|V|W|w|x|X|y|Y|z)/g,
  date_bbreviatedWeekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat'],
  date_fullWeekdays: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  date_abbreviatedMonths: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  date_fullMonths: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
  
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
    if (date.getHours() > 12) {
      return date.getHours() - 12;
    } else {
      return date.getHours();
    }
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
        case 'a':
          return self.dates_abbreviatedWeekdays[date.getDay()];
        case 'A':
          return self.dates_fullWeekdays[date.getDay()];
        case 'b':
          return self.dates_abbreviatedMonths[date.getMonth()];
        case 'B':
          return self.dates_fullMonths[date.getMonth()];
        case 'c':
          return date.toLocaleString();
        case 'C':
          return Math.round(date.getFullYear() / 100);
        case 'd':
          return self.padNumber(date.getDate(), 2);
        case 'D':
          return self.format(date, '%m/%d/%y');
        case 'e':
          return self.padNumber(date.getDate(), 2, ' ');
        case 'F':
          return self.format(date, '%Y-%m-%d');
        case 'h':
          return self.format(date, '%b');
        case 'H':
          return self.padNumber(date.getHours(), 2);
        case 'I':
          return self.padNumber(self.tweleveHour(date), 2);
        case 'j':
          return self.padNumber(self.dayOfYear(date), 3);
        case 'k':
          return self.padNumber(date.getHours(), 2, ' ');
        case 'l':
          return self.padNumber(self.tweleveHour(date), 2, ' ');
        case 'L':
          return self.padNumber(date.getMilliseconds(), 3);
        case 'm':
          return self.padNumber(date.getMonth() + 1, 2);
        case 'M':
          return self.padNumber(date.getMinutes(), 2);
        case 'n':
          return '\n';
        case 'p':
          if (date.getHours() > 11) {
            return 'PM';
          } else {
            return 'AM';
          }
        break;
        case 'P':
          return self.format(date, '%p').toLowerCase();
        case 'r':
          return self.format(date, '%I:%M:%S %p');
        case 'R':
          return self.format(date, '%H:%M');
        case 's':
          return date.getTime() / 1000;
        case 'S':
          return self.padNumber(date.getSeconds(), 2);
        case 't':
          return '\t';
        case 'T':
          return self.format(date, '%H:%M:%S');
        case 'u':
          if (date.getDay() === 0) {
            return 7;
          } else {
            return date.getDay();
          }
          break;
        case 'U':
          return self.padNumber(self.weekOfYear(date), 2);
        case 'v':
          return self.format(date, '%e-%b-%Y');
        case 'V':
          return self.padNumber(self.isoWeekOfYear(date), 2);
        case 'W':
          return self.padNumber(self.weekOfYear(date), 2);
        case 'w':
          return self.padNumber(date.getDay(), 2);
        case 'x':
          return date.toLocaleDateString();
        case 'X':
          return date.toLocaleTimeString();
        case 'y':
          return String(date.getFullYear()).substring(2);
        case 'Y':
          return date.getFullYear();
        case 'z':
          return self.timeZoneOffset(date);
        default:
          return match;
      }
    });
  },
  
};


var helpers = {

  // -----------------------------
  // Collection Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-collections.js
  // -----------------------------

  /**
   * {{any}}
   * @param  {Array}  array
   * @param  {Object} options
   */
  any: function (array, options) {
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
  after: function (array, count) {
    return array.slice(count);
  },


  /**
   * Use all of the items in the collection after the specified count
   * inside a block.
   * @param  {Array}  array
   * @param  {Number} count
   * @param  {Ojbect} options
   * @return {Array}
   */
  withAfter: function (array, count, options) {
    array = array.slice(count);
    var result = '';
    for (var item in array) {
      result += options.fn(array[item]);
    }
    return result;
  },


  /**
   * {{arrayify}}
   * Converts a string such as "foo, bar, baz" to an ES Array of strings.
   * @credit: http://bit.ly/1840DsB
   * @param  {[type]} data [description]
   * @return {[type]}      [description]
   */
  arrayify: function (str) {
    return str.split(",").map(function (tag) {
      return "\"" + tag + "\"";
    });
  },


  /**
   * Returns all of the items in the collection before the specified
   * count. Opposite of {{after}}.
   * @param  {Array}  array [description]
   * @param  {[type]} count [description]
   * @return {[type]}       [description]
   */
  before: function (array, count) {
    return array.slice(0, -count);
  },


  /**
   * Use all of the items in the collection before the specified count
   * inside a block. Opposite of {{withAfter}}
   * @param  {Array}  array   [description]
   * @param  {[type]} count   [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   */
  withBefore: function (array, count, options) {
    array = array.slice(0, -count);
    var result = '';
    for (var item in array) {
      result += options.fn(array[item]);
    }
    return result;
  },


  /**
   * {{first}}
   * Returns the first item in a collection.
   *
   * @param  {Array}  array
   * @param  {[type]} count
   * @return {[type]}
   */
  first: function (array, count) {
    if (helperutils.isUndefined(count)) {
      return array[0];
    } else {
      return array.slice(0, count);
    }
  },

  /**
   * {{withFirst}}
   * Use the first item in a collection inside a block.
   *
   * @param  {Array}  array   [description]
   * @param  {[type]} count   [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
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
   * @param  {Array}  array [description]
   * @param  {[type]} count [description]
   * @return {[type]}       [description]
   */
  last: function (array, count) {
    if (helperutils.isUndefined(count)) {
      return array[array.length - 1];
    } else {
      return array.slice(-count);
    }
  },

  /**
   * Use the last item in a collection inside a block.
   * Opposite of {{withFirst}}.
   * @param  {Array}  array   [description]
   * @param  {[type]} count   [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   */
  withLast: function (array, count, options) {
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
   * @param  {Array}  array     [description]
   * @param  {[type]} separator [description]
   * @return {[type]}           [description]
   */
  join: function (array, separator) {
    return array.join(helperutils.isUndefined(separator) ? ' ' : separator);
  },


  /**
   * Handlebars "joinAny" block helper that supports
   * arrays of objects or strings. implementation found here:
   * https://github.com/wycats/handlebars.js/issues/133
   *
   * @param  {[type]} items [description]
   * @param  {[type]} block [description]
   * @return {[type]}       [description]
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
  joinAny: function (items, block) {
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


  sort: function (array, field) {
    if (helperutils.isUndefined(field)) {
      return array.sort();
    } else {
      return array.sort(function (a, b) {
        return a[field] > b[field];
      });
    }
  },


  withSort: function (array, field, options) {
    array = _.cloneDeep(array);
    var getDescendantProp = function (obj, desc) {
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
      array = array.sort(function (a, b) {
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


  length: function (array) {
    return (!array) ? 0 : array.length;
  },


  lengthEqual: function (array, length, options) {
    if (array.length === length) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },


  empty: function (array, options) {
    if (array.length <= 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },


  /**
   * {{inArray}}
   *
   * @param  {Array}  array   [description]
   * @param  {[type]} value   [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   */
  inArray: function (array, value, options) {
    var _indexOf = require('../utils/lib/indexOf');
    if (_indexOf.call(array, value) >= 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },


  /**
   * {{filter}}
   * @param  {[type]} array   [description]
   * @param  {[type]} value   [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   */
  filter: function(array, value, options) {

    var data = void 0;
    var content = '';
    var results = [];

    if(options.data) {
      data = Handlebars.createFrame(options.data);
    }

    // filtering on a specific property
    if(options.hash && options.hash.property) {

      var search = {};
      search[options.hash.property] = value;
      results = _.filter(array, search);

    } else {

      // filtering on a string value
      results = _.filter(array, function(v, k) {
        return value === v;
      });

    }

    if(results && results.length > 0) {
      for(var i=0; i < results.length; i++){
        content += options.fn(results[i], {data: data});
      }
    } else {
      content = options.inverse(this);
    }
    return content;
  },

  /**
   * {{iterate}}
   *
   * Similar to {{#each}} helper, but treats array-like objects
   * as arrays (e.g. objects with a `.length` property that
   * is a number) rather than objects. This lets us iterate
   * over our collections items.
   *
   * @param  {[type]} context [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   */
  iterate: function (context, options) {
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
   * {{forEach}}
   * Credit: http://bit.ly/14HLaDR
   *
   * @param  {[type]}   array [description]
   * @param  {Function} fn    [description]
   * @return {[type]}         [description]
   *
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
  forEach: function (array, fn) {
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
   * {{eachProperty}}
   * Handlebars block helper to enumerate
   * the properties in an object
   *
   * @param  {[type]} context [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   */
  eachProperty: function (context, options) {
    var content = (function () {
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
   * {{eachIndex}}
   *
   * @param  {Array}  array   [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   * @example:
   *   {{#eachIndex collection}}
   *     {{item}} is {{index}}
   *   {{/eachIndex}}
   */
  eachIndex: function (array, options) {
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

  /**
   * {{eachIndexPlusOne}}
   *
   * @param  {Array}  array   [description]
   * @param  {Object} options [description]
   * @return {[type]}         [description]
   * @example:
   *   {{#eachIndexPlusOne collection}}
   *     {{item}} is {{index}}
   *   {{/eachIndexPlusOne}}
   */
  eachIndexPlusOne: function (array, options) {
    var result = '';
    var len;
    var i;
    var index;
    for (index = i = 0, len = array.length; i < len; index = ++i) {
      var value = array[index];
      result += options.fn({
        item: value,
        index: index + 1
      });
    }
    return result;
  },

  // -----------------------------
  // Comparison Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-comparisons.js
  // -----------------------------

  contains: function (str, pattern, options) {
    if (str.indexOf(pattern) !== -1) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  and: function (a, b, options) {
    if (a && b) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  gt: function (value, test, options) {
    if (value > test) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  gte: function (value, test, options) {
    if (value >= test) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  is: function (value, test, options) {
    if (value === test) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  isnt: function (value, test, options) {
    if (value !== test) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  lt: function (value, test, options) {
    if (value < test) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  lte: function (value, test, options) {
    if (value <= test) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  /**
   * Or
   * Conditionally render a block if one of the values is truthy.
   */
  or: function (a, b, options) {
    if (a || b) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  /**
   * ifNth
   * Conditionally render a block if mod(nr, v) is 0
   */
  ifNth: function (nr, v, options) {
    v = v+1;
    if (v % nr === 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },

  /**
   * {{#compare}}...{{/compare}}
   *
   * @credit: OOCSS
   * @param left value
   * @param operator The operator, must be between quotes ">", "=", "<=", etc...
   * @param right value
   * @param options option object sent by handlebars
   * @return {String} formatted html
   *
   * @example:
   *   {{#compare unicorns "<" ponies}}
   *     I knew it, unicorns are just low-quality ponies!
   *   {{/compare}}
   *
   *   {{#compare value ">=" 10}}
   *     The value is greater or equal than 10
   *     {{else}}
   *     The value is lower than 10
   *   {{/compare}}
   */
  compare: function(left, operator, right, options) {
    /*jshint eqeqeq: false*/

    if (arguments.length < 3) {
      throw new Error('Handlebars Helper "compare" needs 2 parameters');
    }

    if (options === undefined) {
      options = right;
      right = operator;
      operator = '===';
    }

    var operators = {
      '==':     function(l, r) {return l == r; },
      '===':    function(l, r) {return l === r; },
      '!=':     function(l, r) {return l != r; },
      '!==':    function(l, r) {return l !== r; },
      '<':      function(l, r) {return l < r; },
      '>':      function(l, r) {return l > r; },
      '<=':     function(l, r) {return l <= r; },
      '>=':     function(l, r) {return l >= r; },
      'typeof': function(l, r) {return typeof l == r; }
    };

    if (!operators[operator]) {
      throw new Error('Handlebars Helper "compare" doesn\'t know the operator ' + operator);
    }

    var result = operators[operator](left, right);

    if (result) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },


  /**
   * {{if_eq}}
   *
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{if_eq this compare=that}}
   */
  if_eq: function (context, options) {
    if (context === options.hash.compare) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  /**
   * {{unless_eq}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{unless_eq this compare=that}}
   */
  unless_eq: function (context, options) {
    if (context === options.hash.compare) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * {{if_gt}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{if_gt this compare=that}}
   */
  if_gt: function (context, options) {
    if (context > options.hash.compare) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  /**
   * {{unless_gt}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{unless_gt this compare=that}}
   */
  unless_gt: function (context, options) {
    if (context > options.hash.compare) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * {{if_lt}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{if_lt this compare=that}}
   */
  if_lt: function (context, options) {
    if (context < options.hash.compare) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  /**
   * {{unless_lt}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{unless_lt this compare=that}}
   */
  unless_lt: function (context, options) {
    if (context < options.hash.compare) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * {{if_gteq}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{if_gteq this compare=that}}
   */
  if_gteq: function (context, options) {
    if (context >= options.hash.compare) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  /**
   * {{unless_gteq}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{unless_gteq this compare=that}}
   */
  unless_gteq: function (context, options) {
    if (context >= options.hash.compare) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * {{if_lteq}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{if_lteq this compare=that}}
   */
  if_lteq: function (context, options) {
    if (context <= options.hash.compare) {
      return options.fn(this);
    }
    return options.inverse(this);
  },

  /**
   * {{unless_lteq}}
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{unless_lteq this compare=that}}
   */
  unless_lteq: function (context, options) {
    if (context <= options.hash.compare) {
      return options.inverse(this);
    }
    return options.fn(this);
  },

  /**
   * {{ifAny}}
   * Similar to {{#if}} block helper but accepts multiple arguments.
   * @author: Dan Harper <http://github.com/danharper>
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{ifAny this compare=that}}
   */
  ifAny: function () {
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
    } else {
      return content.inverse(this);
    }
  },

  /**
   * {{ifEven}}
   * Determine whether or not the @index is an even number or not
   * @author: Stack Overflow Answer <http://stackoverflow.com/questions/18976274/odd-and-even-number-comparison-helper-for-handlebars/18993156#18993156>
   * @author: Michael Sheedy <http://github.com/sheedy> (found code and added to repo)
   *
   * @param  {[type]} context [description]
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   *
   * @example: {{ifEven @index}}
   */
  ifEven: function (conditional, options) {
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
   * {{formatData}}
   * Port of formatDate-js library (http://bit.ly/18eo2xw)
   * @param  {[type]} date   [description]
   * @param  {[type]} format [description]
   * @return {[type]}        [description]
   */
  formatDate: function (date, format) {
    date = new Date(date);
    return helperutils.format(date, format);
  },

  /**
   * {{now}}
   * @param  {[type]} format [description]
   * @return {[type]}        [description]
   */
  now: function (format) {
    var date = new Date();
    if (helperutils.isUndefined(format)) {
      return date;
    } else {
      return helperutils.format(date, format);
    }
  },

  /**
   * {{timeago}}
   * Modified version of http://bit.ly/18WwJYf
   * @param  {[type]} date [description]
   * @return {[type]}      [description]
   */
  timeago: function (date) {
    date = new Date(date);
    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = Math.floor(seconds / 31536000);
    if (interval > 1) {return "" + interval + " years ago"; }
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) {return "" + interval + " months ago"; }
    interval = Math.floor(seconds / 86400);
    if (interval > 1) {return "" + interval + " days ago"; }
    interval = Math.floor(seconds / 3600);
    if (interval > 1) {return "" + interval + " hours ago"; }
    interval = Math.floor(seconds / 60);
    if (interval > 1) {return "" + interval + " minutes ago"; }
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
  
  log: function (value) {
    return console.log(value);
  },
  
  // -----------------------------
  // Math Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-math.js
  // -----------------------------
  
  add: function (value, addition) {
    return value + addition;
  },

  subtract: function (value, substraction) {
    return value - substraction;
  },

  divide: function (value, divisor) {
    return value / divisor;
  },

  multiply: function (value, multiplier) {
    return value * multiplier;
  },

  floor: function (value) {
    return Math.floor(value);
  },

  ceil: function (value) {
    return Math.ceil(value);
  },

  round: function (value) {
    return Math.round(value);
  },

  // Attempt to parse the int, if not class it as 0
  sum: function () {
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
  
  default: function (value, defaultValue) {
    return value !== null ? value : defaultValue;
  },

  /**
   * http://handlebarsjs.com/block_helpers.html
   * @param  {[type]} options [description]
   * @return {[type]}         [description]
   */
  noop: function (options) {
    return options.fn(this);
  },

  /**
   * {{#withHash}}
   * Build context from the attributes hash
   * @author Vladimir Kuznetsov <https://github.com/mistakster>
   */
  withHash: function (options) {
    return options.fn(options.hash || {});
  },
  
  // -----------------------------
  // Number Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-numbers.js
  // -----------------------------
  
  /**
   * {{addCommas}}
   *
   * Add commas to numbers
   * @param {[type]} number [description]
   */
  addCommas: function (number) {
    return number.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
  },

 /**
  * {{formatPhoneNumber number}}
  * Output a formatted phone number
  * @author: http://bit.ly/QlPmPr
  * @param  {Number} phoneNumber [8005551212]
  * @return {Number}             [(800) 555-1212]
  */
  formatPhoneNumber: function (num) {
    num = num.toString();
    return "(" + num.substr(0, 3) + ") " + num.substr(3, 3) + "-" + num.substr(6, 4);
  },

  /**
   * {{random}}
   * Generate a random number between two values
   * @author Tim Douglas <https://github.com/timdouglas>
   * @param  {[type]} min [description]
   * @param  {[type]} max [description]
   * @return {[type]}     [description]
   */
  random: function (min, max) {
    return _.random(min, max);
  },

  /**
   * {{toAbbr}}
   *
   * Abbreviate numbers
   * @param  {[type]} number [description]
   * @param  {[type]} digits [description]
   * @return {[type]}        [description]
   */
  toAbbr: function (number, digits) {
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

  toExponential: function (number, fractions) {
    if (helperutils.isUndefined(fractions)) {
      fractions = 0;
    }
    return number.toExponential(fractions);
  },

  toFixed: function (number, digits) {
    if (helperutils.isUndefined(digits)) {
      digits = 0;
    }
    return number.toFixed(digits);
  },

  toFloat: function (number) {
    return parseFloat(number);
  },

  toInt: function (number) {
    return parseInt(number, 10);
  },

  toPrecision: function (number, precision) {
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
   * {{capitalizeFirst}}
   * Capitalize first word in a sentence
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  capitalizeFirst: function (str) {
    if(str && typeof str === "string") {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
  },

  /**
   * {{capitalizeEach}}
   * Capitalize each word in a sentence
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  capitalizeEach: function (str) {
    if(str && typeof str === "string") {
      return str.replace(/\w\S*/g, function (word) {
        return word.charAt(0).toUpperCase() + word.substr(1);
      });
    }
  },

  /**
   * {{center}}
   * Center a string using non-breaking spaces
   * @param  {[type]} str    [description]
   * @param  {[type]} spaces [description]
   * @return {[type]}        [description]
   */
  center: function (str, spaces) {
    if(str && typeof str === "string") {
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
   * {{dashify}}
   * Replace periods in string with hyphens.
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  dashify: function (str) {
    if(str && typeof str === "string") {
      return str.split(".").join("-");
    }
  },

  /**
   * {{hyphenate}}
   * Replace spaces in string with hyphens.
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  hyphenate: function (str) {
    if(str && typeof str === "string") {
      return str.split(" ").join("-");
    }
  },

  /**
   * {{lowercase}}
   * Make all letters in the string lowercase
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  lowercase: function (str) {
    if(str && typeof str === "string") {
      return str.toLowerCase();
    }
  },
  
  /**
   * {{plusify}}
   * Replace spaces in string with pluses.
   * @author: Stephen Way <https://github.com/stephenway>
   * @param  {[type]} str The input string
   * @return {[type]}     Input string with spaces replaced by plus signs
   */
  plusify: function (str) {
    if(str && typeof str === "string") {
      return str.split(" ").join("+");
    }
  },

  /**
   * {{safeString}}
   * Output a Handlebars safeString
   * @param  {[type]} str [description]
   * @return {[type]}       [description]
   */
  safeString: function (str) {
    if(str && typeof str === "string") {
      return new helperutils.safeString(str);
    }
  },

  /**
   * {{sentence}}
   * Sentence case
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  sentence: function (str) {
    if(str && typeof str === "string") {
      return str.replace(/((?:\S[^\.\?\!]*)[\.\?\!]*)/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
    }
  },

  /**
   * {{titleize}}
   * Title case. "This is Title Case"
   * @param  {[type]} str [description]
   * @return {[type]}     [description]
   */
  titleize: function (str) {
    if(str && typeof str === "string") {
      var title = str.replace(/[ \-_]+/g, ' ');
      var words = title.match(/\w+/g);
      var capitalize = function (word) {
        return word.charAt(0).toUpperCase() + word.slice(1);
      };
      return ((function () {
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

  uppercase: function (options) {
    if(options && typeof options === "string") {
      return options.toUpperCase();
    } else if(options && typeof options === "object") {
      return options.fn(this).toUpperCase();
    }
  },

  reverse: function (str) {
    if(str && typeof str === "string") {
      return str.split('').reverse().join('');
    }
  },

  /**
   * {{count}}
   * Return the number of occurrances of a string, within a string
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {String} str       The haystack
   * @param  {String} substring The needle
   * @return {Number}           The number of times the needle is found in the haystack.
   */
  count: function (str, substring) {
    if(str && typeof str === "string") {
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
   * {{replace}}
   * Replace occurrences of string "A" with string "B"
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {[type]} str [description]
   * @param  {[type]} a   [description]
   * @param  {[type]} b   [description]
   * @return {[type]}     [description]
   */
  replace: function (str, a, b) {
    if(str && typeof str === "string") {
      return str.split(a).join(b);
    }
  },

  /**
   * {{ellipsis}}
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * Truncate the input string and removes all HTML tags
   * @param  {String} str      The input string.
   * @param  {Number} limit    The number of characters to limit the string.
   * @param  {String} append   The string to append if charaters are omitted.
   * @return {String}          The truncated string.
   */
  ellipsis: function (str, limit, append) {
    if (helperutils.isUndefined(append)) {
      append = '';
    }
    var sanitized = str.replace(/(<([^>]+)>)/g, '');
    if (sanitized.length > limit) {
      return sanitized.substr(0, limit - append.length) + append;
    } else {
      return sanitized;
    }
  },

  /**
   * {{truncate}}
   * Truncates a string given a specified `length`,
   * providing a custom string to denote an `omission`.
   * @param  {[type]} str      [description]
   * @param  {[type]} length   [description]
   * @param  {[type]} omission [description]
   * @return {[type]}          [description]
   */
  truncate: function (str, limit, omission) {
    if (helperutils.isUndefined(omission)) {
      omission = '';
    }
    if (str.length > limit) {
      return str.substring(0, limit - omission.length) + omission;
    } else {
      return str;
    }
  },

  /**
   * {{startsWith}}
   * @author: Dan Fox <http://github.com/iamdanfox>
   *
   * Tests whether a string begins with the given prefix.
   * Behaves sensibly if the string is null.
   * @param  {[type]} prefix     [description]
   * @param  {[type]} testString [description]
   * @param  {[type]} options    [description]
   * @return {[type]}            [description]
   *
   * @example:
   *   {{#startsWith "Goodbye" "Hello, world!"}}
   *     Whoops
   *   {{else}}
   *     Bro, do you even hello world?
   *   {{/startsWith}}
   */
  startsWith: function (prefix, str, options) {
    if ((str !== null ? str.indexOf(prefix) : void 0) === 0) {
      return options.fn(this);
    } else {
      return options.inverse(this);
    }
  },
  
  // -----------------------------
  // URL Helpers
  // https://github.com/assemble/handlebars-helpers/blob/master/lib/helpers/helpers-url.js
  // -----------------------------
  
  stripQuerystring: function (url) {
    return url.split("?")[0];
  },

  /**
   * {{encodeURI}}
   * Encodes a Uniform Resource Identifier (URI) component
   * by replacing each instance of certain characters by
   * one, two, three, or four escape sequences representing
   * the UTF-8 encoding of the character.
   *
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {String} uri: The un-encoded string
   * @return {String}      The endcoded string.
   */
  encodeURI: function (uri) {
    return encodeURIComponent(uri);
  },

  /**
   * {{decodeURI}}
   * Decodes a Uniform Resource Identifier (URI) component
   * previously created by encodeURIComponent or by a
   * similar routine.
   *
   * @author: Jon Schlinkert <http://github.com/jonschlinkert>
   * @param  {[type]} encodedURI [description]
   * @return {[type]}            [description]
   */
  decodeURI: function (encodedURI) {
    return decodeURIComponent(encodedURI);
  },

};

for (var helper in helpers) {
  if (helpers.hasOwnProperty(helper)) {
    Handlebars.registerHelper(helper, helpers[helper]);
  }
}
