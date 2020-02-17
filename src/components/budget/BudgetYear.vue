<template>
  <div id='budgetyear'>
    <h3>Past Year Budget</h3>
    <div class='tablewrap'>
      <table cellpadding='0' cellspacing='0'>
        <thead><tr>
          <th class='category'><div>Category</div></th>
          <th class='month usdint' v-for='month in months' :key='month.format("YYYY-MM")'>
            <div>{{month.format("MMM")}}</div>
          </th>
          <th class='average usdint'><div>Average</div></th>
          <th class='total usdint'><div>Total</div></th>
        </tr></thead>
        <tbody v-if='groups'>
          <!-- Category Rows -->
          <tr v-for='cat in this.categories' :key='"cat-"+cat.id' class='category'>
            <td class='category'><div>{{cat.name}}</div></td>
            <td class='month usdint' v-for='monthstr in monthstrs' :key='cat.name+monthstr'>
              <BudgetYearCell :groups='groups' :cat='cat' :monthstr='monthstr'/>
            </td>
            <td class='average usdint'><div>{{ avgCategory(cat.name) | usdint(0) }}</div></td>
            <td class='total usdint'><div>{{ groups[cat.name].total | usdint(0) }}</div></td>
          </tr>
          <!-- Totals -->
          <tr class='savings'>
            <td class='category'><div>Savings</div></td>
            <td class='month usdint' v-for='monthstr in monthstrs' :key='"total"+monthstr'>
              <div>{{sumMonthSpending(monthstr) | usdint(0) }}</div>
            </td>
            <td class='average usdint'><div>--</div></td>
            <td class='total usdint'><div>--</div></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import * as _ from 'lodash';
  import * as api from '@/api';
  import * as moment from 'moment';
  import * as pathify from 'vuex-pathify';
  import BudgetYearCell from './BudgetYearCell';

  export default {
    name: 'BudgetYear',
    components: {BudgetYearCell},
    data: () => ({
      transactions: {},                   // Displayed transactions
      groups: null,                       // Grouped Transactions {catname -> month -> [trxs]}
      start: moment().startOf('month'),   // Starting month
      uncategorized: 'Uncategorized',     // Uncategorized label
    }),
    watch: {
      account: { immediate:true, handler:function() {
        this.updateTransactions();
      }},
    },
    computed: {
      categories: pathify.sync('budget/categories'),
      monthstrs: function() { return _.map(this.months, month => month.format('YYYY-MM')); },
      months: function() {
        var months = [];
        var month = this.start.clone();
        for (var i=0; i<=12; i++) {
          months.push(month.clone());
          month.subtract(1, 'months');
        }
        return months;
      },
    },
    methods: {
      // Update Transactions
      // Search for and update the list of displayed transactions
      updateTransactions: async function() {
        this.cancelSearch = api.cancel(this.cancelSearch);
        var mindatestr = this.start.clone().subtract(12, 'months').format('YYYY-MM-DD');
        var token = this.cancelSearch.token;
        var params = {search:`date>=${mindatestr}`, limit:9999};
        var {data} = await api.Budget.getTransactions(params, token);
        this.transactions = data.results;
        this.groupTransactions();
      },

      // Init Groups
      // Initialize an empty group collection
      initGroups: function() {
        var groups = {};
        var catnames = _.map(this.categories, 'name');
        for (var catname of catnames) {
          groups[catname] = {};
          groups[catname].total = 0;
          groups[catname].count = 0;
          for (var month of this.months) {
            groups[catname][month.format('YYYY-MM')] = [];
          }
        }
        return groups;
      },

      // Group Transactions
      // Sort transactions by category and month
      groupTransactions: function() {
        var groups = this.initGroups();
        for (var trx of this.transactions) {
          var month = moment(trx.date).startOf('month');
          var monthstr = month.format('YYYY-MM');
          groups[trx.category.name][monthstr].push(trx);
          groups[trx.category.name].total += parseFloat(trx.amount);
          groups[trx.category.name].count += 1;
        }
        this.groups = groups;
      },

      // Avg Category (horizontal)
      // Average spending for all months in the specified category
      avgCategory: function(catname) {
        if (!this.groups[catname].count) { return 0; }
        return this.groups[catname].total / 12.0;
      },

      // Sum Month Spending (vertical)
      // Sum the spending for the specified month
      sumMonthSpending: function(monthstr) {
        var total = 0;
        for (var catname in this.groups) {
          if (catname == 'Ignored') { continue; }
          for (var trx of this.groups[catname][monthstr]) {
            total += parseFloat(trx.amount);
          }
        }
        return total;
      },

    }
  };
</script>

<style lang='scss'>
  #budgetyear {
    padding: 10px 20px;
    th, td {
      // Specific column widths
      &.category { width:14%; }
      &.trend { width:6%; }
      &.budget { width:9%; }
      &.month { width:5%; }  // 12 of these
      &.average { width:6%; }
      &.total { width:6%; }
    }
  }
</style>
