<template>
  <div id='budgetmenu'>
    <!-- Budget -->
    <div class='item' @click='view="month"; account=null' :class='{highlighted:view=="month"}'>
      <i class='mdi mdi-email-outline'/>Budget
    </div>
    <div class='submenu'>
      <div class='subitem' :class='{highlighted:view=="year"}' @click='view="year"; account=null'>
        <div class='name'>Past Year</div>
        <div v-if='summary' class='balance blur'>{{summary.pastyear.total | usdint}}</div>
        <div v-if='summary' class='subtext' style='float:right'>saved</div>
        <div v-if='summary' class='subtext' style='float:left; clear:left;'>{{summary.pastyear.transactions | intcomma}} transactions</div>
        <div style='clear:both'/>
      </div>
    </div>
    <!-- Accounts -->
    <div class='item' @click='view="transactions"; account=null'
      :class='{highlighted:view=="transactions" && !account}'>
      <i class='mdi mdi-bank-outline'/>Transactions
    </div>
    <div class='submenu'>
      <div class='subitem account' v-for='acct in displayAccounts' :key='acct.id'
        :class='{highlighted:view=="transactions" && acct==account}'
        @click='view="transactions"; account=acct'>
          <div class='name'>{{acct.name}}</div>
          <div class='balance blur'>{{acct.balance | usdint}}</div>
          <div class='subtext updated'>{{acct.balancedt | timeAgo}}</div>
      </div>
      <div class='total blur'>{{balance | usdint}}</div>
      <div style='clear:both;'/>
    </div>
    <!-- Settings -->
    <div class='item' @click='view="settings"; account=null' :class='{highlighted:view=="settings"}'>
      <i class='mdi mdi-cogs'/>Settings
    </div>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import sumBy from 'lodash/sumBy';
  
  export default {
    name: 'BudgetMenu',
    computed: {
      view: pathify.sync('budget/view'),
      account: pathify.sync('budget/account'),
      accounts: pathify.get('budget/accounts'),
      summary: pathify.get('budget/summary'),
      displayAccounts: function() { return this.accounts.filter(a => a.id); },
      balance: function() { return sumBy(this.accounts, a => parseFloat(a.balance) || 0).toFixed(2); },
    },
    // watch: {
    //   $route (to, from) { console.log(`Changed! ${from} -> ${to}`); },
    // } 
  };
</script>

<style lang='scss'>

  #budgetmenu .item,
  #budgetmenu .subitem {
    border-bottom-right-radius: 8px;
    border-left: 3px solid transparent;
    border-top-right-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    overflow: hidden;
    padding: 10px;
    position: relative;
    text-overflow: ellipsis;
    user-select: none;
    white-space: nowrap;
    &.highlighted, &:hover {
      border-left: 3px solid $darkbg-accent;
      background-color: lighten($darkbg-color, 5%);
    }
  }
  #budgetmenu .item {
    font-size: 16px;
    margin-top: 10px;
    padding: 15px 15px 15px 45px;
    .mdi {
      font-size: 1.3em;
      left: 15px;
      position: absolute;
      top: calc(50% - 15px);
    }
  }
  #budgetmenu .subitem {
    font-size: 13px;
    padding: 5px 15px 5px 45px;
    .name { float:left; }
    .balance { float:right; font-family:$fontfamily-code; }
    .subtext { clear:both; color:$darkbg-fg4; font-size:9px; font-weight:400; }
  }
  #budgetmenu .total {
    float: right;
    font-size: 0.8rem;
    font-family: $fontfamily-code;
    font-weight: 400;
    margin-right: 15px;
    margin-top: 1px;
    padding: 3px 0px;
    border-top: 1px solid lighten($darkbg-bg0, 20%);
  }
</style>
