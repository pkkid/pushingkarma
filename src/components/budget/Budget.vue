<template>
  <div id='budget'>
    <Navigation :cls="'topnav'" />
    <div id='sidebar'>
      <div class='menuitem'><i class='mdi mdi-email-outline'/>Budget</div>
      <div class='menuitem'><i class='mdi mdi-bank-outline'/>Accounts</div>
      <div class='submenu'>
        <div class='menuitem' v-for='account in accounts' :key='account.fid'>
          {{account.name}}
          {{account.balancedt}}
        </div>
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
  import {axios, makeRequest} from '@/utils/utils';
  import {sync} from 'vuex-pathify';

  var API_ACCOUNTS = '/api/accounts';

  export default {
    name: 'Budget',
    components: {Navigation, Footer},
    computed: {
      accounts: sync('budget/accounts'),
      transactions: sync('budget/transactions'),
    },
    data: () => ({
      request_accounts: null,
    }),
    
    mounted: function() {
      this.$store.set('global/layout', 'topnav');
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
</style>
