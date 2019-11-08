<template>
  <div id='sidebar'>
    <div class='menuitem' @click='view="budget"' :class='{highlighted:view=="budget"}'>
      <i class='mdi mdi-email-outline'/>Budget
    </div>
    <div class='menuitem' @click='view="transactions"; viewAccount="all"'
      :class='{highlighted:view=="transactions" && viewAccount=="all"}'>
      <i class='mdi mdi-bank-outline'/>All Accounts
    </div>
    <div class='submenu'>
      <div class='submenuitem account' v-for='account in accounts' :key='account.id'
        :class='{highlighted:view=="transactions" && viewAccount==account.id}'
        @click='view="transactions"; viewAccount=account.id'>
          <div class='name'>{{account.name}}</div>
          <div class='balance blur'>{{account.balance | usdint}}</div>
          <div class='subtext updated'>{{account.balancedt | timeAgo}} ago</div>
      </div>
      <div class='total blur'>{{balance | usdint}}</div>
      <div style='clear:both;'/>
    </div>
  </div>
</template>

<script>
  import * as _ from 'lodash';
  import * as pathify from 'vuex-pathify';
  
  export default {
    name: 'BudgetAccounts',
    data: () => ({
      balance: 0,
    }),
    computed: {
      view: pathify.sync('budget/view'),
      viewAccount: pathify.sync('budget/viewAccount'),
      accounts: pathify.sync('budget/accounts'),
    },
    watch: {
      // Watch Accounts
      // Update balance
      accounts: function() {
        var balances = this.accounts.map((a) => { return parseFloat(a.balance); });
        this.balance = _.sum(balances).toFixed(2);
      }
    }
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
