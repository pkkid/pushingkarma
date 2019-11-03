<template>
  <div class='submenu'>
    <div class='menuitem account' v-for='account in accounts' :key='account.fid'>
      <div class='name'>{{account.name}}</div>
      <div class='balance blur'>{{account.balance | usdint}}</div>
      <div class='updated'>{{account.balancedt | timeAgo}} ago</div>
    </div>
    <div class='total'>{{balance | usdint}}</div>
    <div style='clear:both;'/>
  </div>
</template>

<script>
  import {sum} from 'lodash';
  import {sync} from 'vuex-pathify';
  export default {
    name: 'BudgetAccounts',
    data: () => ({
      balance: 0,
    }),
    computed: {
      accounts: sync('budget/accounts'),
    },
    watch: {
      accounts: function() {
        var balances = this.accounts.map((a) => { return parseFloat(a.balance); });
        this.balance = sum(balances).toFixed(2);
      }
    },
  };
</script>

<style lang='scss'>
  #budget #sidebar {
    .menuitem.account {
      line-height: 1em;
      font-size: 0.9em;
      color: darken($darkbg-text, 10%);
      margin-top: 10px;
      .name {
        float: left;
        padding-left: 32px;
      }
      .updated {
        font-size: .6em; 
        clear: both;
        padding-left: 32px;
        color: darken($darkbg-text, 50%);
      }
      .balance { float: right; }
      &:first-child { margin-top: 5px; }
    }
    .total {
      color: darken($darkbg-text, 10%);
      float: right;
      font-size: 0.7em;
      font-weight: 600;
      margin-right: -5px;
      padding: 3px 5px;
      border-top: 1px solid darken($darkbg-text, 60%);
    }
  }
</style>
