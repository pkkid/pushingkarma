<template>
  <div id='budgetmenu'>
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
  import * as pathify from 'vuex-pathify';
  import sumBy from 'lodash/sumBy';
  
  export default {
    name: 'BudgetMenu',
    computed: {
      view: pathify.sync('budget/view'),
      account: pathify.sync('budget/account'),
      accounts: pathify.sync('budget/accounts'),
      balance: function() { return sumBy(this.accounts, a => parseFloat(a.balance)).toFixed(2); },
    },
  };
</script>

<style lang='scss'>
  #budget #budgetmenu {
    font-size: 1rem;
    width: 300px;
    height: calc(100vh - 60px);
    overflow: hidden;
    position: fixed;
    top: 60px;
    padding: 30px 0px;
    overflow-y: hidden;

    // Menu Items
    .menuitem,
    .submenuitem {
      border-bottom-right-radius: 8px;
      border-left: 3px solid transparent;
      border-top-right-radius: 8px;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 500;
      overflow: hidden;
      padding: 15px 15px 15px 12px;
      text-overflow: ellipsis;
      user-select: none;
      white-space: nowrap;
      .subtext {
        font-size: 0.7em;
        font-weight: 400;
        color: $darkbg-text-dim;
        padding-top: 2px;
      }
      &.highlighted,
      &:hover {
        border-left: 3px solid $darkbg-accent;
        background-color: lighten($darkbg-color, 5%);
      }
      .mdi {
        margin-right: 12px;
        font-size: 1.3em;
        position: relative;
        top: 2px;
      }
    }
    .submenuitem {
      font-size: 0.9em;
      padding: 7px 15px 7px 12px;
    }

    // More shit..
    .name {
      float: left;
      padding-left: 32px;
    }
    .subtext {
      clear: both;
      padding-left: 32px;
      font-size: .7em;
      font-weight: 400;
      color: #bdae93;
      padding-top: 2px;
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
</style>
