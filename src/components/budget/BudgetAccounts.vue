<template>
  <div class='submenu'>
    <div class='submenuitem account' v-for='account in accounts' :key='account.fid'>
      <div class='name'>{{account.name}}</div>
      <div class='balance blur'>{{account.balance | usdint}}</div>
      <div class='subtext updated'>{{account.balancedt | timeAgo}} ago</div>
    </div>
    <div class='total'>{{balance | usdint}}</div>
    <div style='clear:both;'/>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import {sum} from 'lodash';
  
  export default {
    name: 'BudgetAccounts',
    data: () => ({
      balance: 0,
    }),
    computed: {
      accounts: pathify.sync('budget/accounts'),
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
  #budget {
    font-size: 1.6rem;
    
    #sidebar {
      .name {
        float: left;
        padding-left: 32px;
      }
      .updated {
        //font-size: 1.0rem; 
        clear: both;
        padding-left: 32px;
      }
      .balance {
        float: right;
      }
      .total {
        color: $darkbg-text-dim;
        float: right;
        font-size: 1.1rem;
        font-weight: 600;
        margin-right: 20px;
        margin-top: 1px;
        padding: 3px 5px;
        border-top: 1px solid rgba($darkbg-text-dim, .2);
      }
    }
  }
</style>
