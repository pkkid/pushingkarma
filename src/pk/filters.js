import Vue from "vue";
import * as moment from 'moment';

Vue.filter('formatDate', function(value, format) {
  return moment(value).format(format);
});
