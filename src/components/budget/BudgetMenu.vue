<template>
  <div id='sidebar'>
    <!-- Budget -->
    <div class='menuitem' @click='view="month"; account=null' :class='{highlighted:view=="month"}'>
      <i class='mdi mdi-email-outline'/>Budget
    </div>
    <div class='submenu'>
      <div class='submenuitem' :class='{highlighted:view=="year"}' @click='view="year"; account=null'>
        <div class='name'>Past Year</div>
        <div class='balance blur'>$00.00</div>
        <div class='subtext'>00 transactions</div>
      </div>
    </div>
    <!-- Accounts -->
    <div class='menuitem' @click='view="transactions"; account=null'
      :class='{highlighted:view=="transactions" && !account}'>
      <i class='mdi mdi-bank-outline'/>Transactions
    </div>
    <div class='submenu'>
      <div class='submenuitem account' v-for='acct in accounts' :key='acct.id'
        :class='{highlighted:view=="transactions" && acct==account}'
        @click='view="transactions"; account=acct'>
          <div class='name'>{{acct.name}}</div>
          <div class='balance blur'>{{acct.balance | usdint}}</div>
          <div class='subtext updated'>{{acct.balancedt | timeAgo}} ago</div>
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
    name: 'BudgetMenu',
    data: () => ({
      balance: 0,
    }),
    computed: {
      view: pathify.sync('budget/view'),
      account: pathify.sync('budget/account'),
      accounts: pathify.sync('budget/accounts'),
    },
    watch: {
      accounts: function() {
        var balances = _.map(this.accounts, a => parseFloat(a.balance));
        this.balance = _.sum(balances).toFixed(2);
      },
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
      .subtext {
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
