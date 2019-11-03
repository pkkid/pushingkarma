<template>
  <div id='budget' :class={demo}>
    <Navigation :cls="'topnav'" />
    <div id='sidebar'>
      <div class='menuitem'><i class='mdi mdi-email-outline'/>Budget</div>
      <div class='menuitem'><i class='mdi mdi-bank-outline'/>All Accounts</div>
      <div class='submenu'>
        <div class='menuitem account' v-for='account in accounts' :key='account.fid'>
          <div class='name'>{{account.name}}</div>
          <div class='balance blur'>{{account.balance | usdint}}</div>
          <div class='updated'>{{account.balancedt | timeAgo}} ago</div>
        </div>
        <div class='total'>{{balance | usdint}}</div>
      </div>
    </div>
    <div class='content'>
      <div class='budgetbg'>
        Heya budget Page!
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import Footer from '../Footer';
  import Navigation from '../Navigation';
  import {sum} from 'lodash';
  import {axios, makeRequest} from '@/utils/utils';
  import {sync} from 'vuex-pathify';

  var API_ACCOUNTS = '/api/accounts';

  export default {
    name: 'Budget',
    components: {Navigation, Footer},
    data: () => ({
      request_accounts: null,
      balance: 0,
    }),
    computed: {
      demo: sync('budget/demo'),
      accounts: sync('budget/accounts'),
      transactions: sync('budget/transactions'),
    },
    watch: {
      accounts: function() {
        var balances = this.accounts.map((a) => { return parseFloat(a.balance); });
        this.balance = sum(balances).toFixed(2);
      }
    },
    
    mounted: function() {
      this.$store.set('global/layout', 'topnav');
      this.demo = this.$route.query.demo == '1';
      this.updateAccounts();
    },

    methods: {
      // Update Accounts
      // Update the list of accounts to display.
      updateAccounts: function() {
        let self = this;
        if (this.request_accounts) { this.request_accounts.cancel(); }
        this.request_accounts = makeRequest(axios.get, API_ACCOUNTS, {search:self.search, page:1});
        this.request_accounts.xhr.then(function(response) {
          self.accounts = response.data.results;
        });
      },
    },
  };
</script>

<style lang='scss'>
  // Sidebar Content
  #budget #sidebar {
    float: left;
    width: 300px;
    height: calc(100vh - 60px);
    overflow: hidden;
    position: fixed;
    top: 60px;
    padding: 30px 20px;
    .menuitem {
      font-weight: 500;
      line-height: 2.2;
      cursor: pointer;
      .mdi {
        margin-right: 12px;
        font-size: 1.3em;
        position: relative;
        top: 2px;
      }
    }
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

  #budget .content {
    box-sizing: border-box;
    color: $lightbg-text;
    margin-left: 300px;
    margin-top: 60px;
    background-color: darken($lightbg-color, 10%);
    
    .budgetbg {
      min-height: calc(100vh - 60px);
    }
  }

  // Demo Mode
  #budget.demo .blur {
    color: transparent !important;
    text-shadow: 0 0 10px rgba($lightbg-text, 1) !important;
  }
  #budget.demo #sidebar .blur {
    color: transparent !important;
    text-shadow: 0 0 10px rgba($darkbg-text, 1) !important;
  }
</style>
