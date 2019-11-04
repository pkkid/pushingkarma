<template>
  <div id='budget' :class={demo}>
    <Navigation :cls="'topnav'" />
    <div id='sidebar'>
      <div class='menuitem'><i class='mdi mdi-email-outline'/>Budget</div>
      <div class='menuitem'><i class='mdi mdi-bank-outline'/>All Accounts</div>
      <BudgetAccounts/>
    </div>
    <div class='content'>
      <div class='budgetbg'>
        <Dropzone @filesDropped='upload'/>
        Heya budget Page!
        <div>Hi Mom</div>
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import BudgetAccounts from './BudgetAccounts';
  import Dropzone from '@/components/Dropzone';
  import Footer from '@/components/site/Footer';
  import Navigation from '@/components/site/Navigation';
  import {BudgetAPI} from '@/api';
  import {axios, makeRequest} from '@/utils/utils';
  import {sync} from 'vuex-pathify';

  var API_ACCOUNTS = '/api/accounts';

  export default {
    name: 'Budget',
    components: {
      BudgetAccounts,
      Dropzone,
      Footer,
      Navigation
    },
    data: () => ({
      request_accounts: null,
    }),
    computed: {
      demo: sync('budget/demo'),
      accounts: sync('budget/accounts'),
      transactions: sync('budget/transactions'),
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

      // Upload
      // Upload dropped files
      upload: async function(formdata) {
        var {data} = await BudgetAPI.upload(formdata);
        console.log(data);
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
  }

  #budget .content {
    box-sizing: border-box;
    color: $lightbg-text;
    margin-left: 300px;
    margin-top: 60px;
    background-color: darken($lightbg-color, 10%);
    
    .budgetbg {
      position: relative;
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
