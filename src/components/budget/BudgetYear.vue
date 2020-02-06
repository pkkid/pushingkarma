<template>
  <div id='budgetmonth'>
    <h3>Past Year Budget</h3>
    <div class='tablewrap'>
      <table cellpadding='0' cellspacing='0'>
        <thead><tr>
          <th class='category'><div>Category</div></th>
          <th class='trend'><div>Trend</div></th>
          <th class='budget'><div>Budget</div></th>
          <th class='month' v-for='month in months' :key='month.format("YYYY-MM")'>
            <div>{{month.format("MMM")}}</div>
          </th>
          <th class='average'><div>Average</div></th>
          <th class='total'><div>Total</div></th>
        </tr></thead>
        <tbody>
          <tr v-for='cat in this.categories' :key='"cat-"+cat.id'>
            <td class='category'><div>{{cat.name}}</div></td>
            <td class='trend'><div>--</div></td>
            <td class='budget'><div>{{cat.budget}}</div></td>
            <td class='month' v-for='(trxs,monthstr) in groups[cat.name]' :key='cat.name+monthstr'>
              <div>{{monthstr}}</div>
            </td>
            <td class='average'><div>--</div></td>
            <td class='total'><div>--</div></td>
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

  export default {
    name: 'BudgetYear',
    data: () => ({
      transactions: {},                   // Displayed transactions
      groups: {},                         // Grouped Transactions
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
        catnames.push(this.uncategorized);
        for (var catname of catnames) {
          groups[catname] = {};
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
          var catname = trx.category ? trx.category.name : this.uncategorized;
          var month = moment(trx.date).startOf('month');
          var monthstr = month.format('YYYY-MM');
          groups[catname][monthstr].push(trx);
        }
        this.groups = groups;
      },
    }
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .tablewrap {
      background-color: white;
      border: 1px solid darken($lightbg-color, 20%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 10px;
      min-width: 1000px;
    }

  }
</style>
