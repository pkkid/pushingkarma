import Vue from 'vue';
import * as moment from 'moment';
import {insertCommas} from '@/utils/utils.js';

Vue.filter('formatDate', function(value, format) {
  return moment(value).format(format);
});

Vue.filter('int', function(value) {
  return parseInt(value, 10);
});

Vue.filter('timeAgo', function(value) {
  var now = moment(new Date());
  var then = moment(value);
  return moment.duration(now.diff(then)).humanize();
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
