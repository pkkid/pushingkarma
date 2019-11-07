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
        <BudgetMonth />
        <BudgetTransactions />
        Heya budget Page!
        <div>Hi Mom</div>
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import * as pathify from 'vuex-pathify';
  import BudgetAccounts from './BudgetAccounts';
  import BudgetMonth from './BudgetMonth';
  import BudgetTransactions from './BudgetTransactions';
  import Dropzone from '@/components/Dropzone';
  import Footer from '@/components/site/Footer';
  import Navigation from '@/components/site/Navigation';
  import {BudgetAPI} from '@/api';

  export default {
    name: 'Budget',
    components: {
      BudgetAccounts,
      BudgetMonth,
      BudgetTransactions,
      Dropzone,
      Footer,
      Navigation
    },
    data: () => ({
      view: 'budget',        // One of {budget, transactions}
      transactions: 'all',   // One of {all, <accountid>}
    }),
    watch: {
      view: function() { },
      transactions: function() { },
    },
    computed: {
      demo: pathify.sync('budget/demo'),
      accounts: pathify.sync('budget/accounts'),
      transactions: pathify.sync('budget/transactions'),
    },
    
    mounted: function() {
      this.$store.set('global/layout', 'topnav');
      this.demo = this.$route.query.demo == '1';
      this.updateAccounts();
    },

    methods: {
      // Update Accounts
      // Update the list of accounts to display.
      updateAccounts: async function() {
        var {data} = await BudgetAPI.listAccounts();
        this.accounts = data.results;
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
