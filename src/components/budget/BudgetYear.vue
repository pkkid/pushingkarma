<template>
  <div id='budgetmonth'>
    <h3>Past Year Budget</h3>
    <div class='tablewrap'>
      Hi Dad!
      <div v-for='group of groups' :key='group.id'>

      </div>
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
      groups: [],                         // Grouped Transactions
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
          var month = this.start.clone();
          var monthstr = month.format('YYYY-MM-DD');
          groups[catname] = {};
          groups[catname][monthstr] = [];
          for (var i=0; i<12; i++) {
            month.subtract(1, 'months');
            monthstr = month.format('YYYY-MM-DD');
            groups[catname][monthstr] = [];
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
          var monthstr = month.format('YYYY-MM-DD');
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
