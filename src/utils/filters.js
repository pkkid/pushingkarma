import Vue from 'vue';
import * as dayjs from 'dayjs';
import * as utils from '@/utils/utils';

var RelativeTime = require('dayjs/plugin/relativeTime');
dayjs.extend(RelativeTime);

Vue.filter('formatDate', utils.formatDate);
Vue.filter('int', utils.int);
Vue.filter('commas', utils.insertCommas);
Vue.filter('timeAgo', utils.timeAgo);
Vue.filter('usd', utils.usd);
Vue.filter('usdint', utils.usdint);
