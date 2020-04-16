<template>
  <div id='budgetmonth'>
    <h2>Budget Settings</h2>
    <div class='contentwrap'>
      <!-- Accounts -->
      <h3>Accounts</h3>
      <table>
        <thead><tr>
          <th>Type</th>
          <th>Name</th>
          <th>FID</th>
          <th>Balance</th>
          <th>Last Transaction</th>
        </tr></thead>
        <tbody>
          <tr v-for='acct in accounts' :key='acct.id'>
            <td>{{acct.type}}</td>
            <td>{{acct.name}}</td>
            <td>{{acct.fid}}</td>
            <td>{{acct.balance}}</td>
            <td>--</td>
          </tr>
        </tbody>
      </table>
      <!-- Categories -->
      <h3>Categories</h3>
      <table>
        <thead><tr>
          <th>Name</th>
          <th>Budget</th>
          <th>Exclude From Budget</th>
          <th>Exclude From Totals</th>
        </tr></thead>
        <tbody>
          <tr v-for='cat in categories' :key='cat.id'>
            <td>{{cat.name}}</td>
            <td>{{cat.budget}}</td>
            <td>--</td>
            <td>--</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';

  export default {
    name: 'BudgetSettings',
    computed: {
      accounts: pathify.sync('budget/accounts'),
      categories: pathify.sync('budget/categories'),
    },
    mounted: function() {
      console.log(this.accounts);
    },
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .contentwrap {
      background-color: white;
      border: 1px solid darken($lightbg-color, 20%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 40px;
    }

  }
</style>
