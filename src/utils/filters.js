import Vue from 'vue';
import * as dayjs from 'dayjs';
import {insertCommas} from '@/utils/utils.js';

var RelativeTime = require('dayjs/plugin/relativeTime');
dayjs.extend(RelativeTime);


Vue.filter('formatDate', function(value, format) {
  return dayjs(value).format(format);
});

Vue.filter('int', function(value) {
  return parseInt(value, 10);
});

Vue.filter('timeAgo', function(value) {
  if (Number.isInteger(value) && value < 99999999999) { value *= 1000; }
  return dayjs(value).fromNow();
});

Vue.filter('usd', function(value) {
  var negative = value < 0;
  value = Math.round(Math.abs(value));
  if (negative) { return '-$'+ insertCommas(value); }
  return '$'+ insertCommas(value);
});

Vue.filter('usdint', function(value, places=2) {
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
});
