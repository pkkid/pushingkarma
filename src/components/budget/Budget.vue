<template>
  <div id='budget' :class={demo}>
    <Navigation :cls="'topnav'" />
    <BudgetMenu/>
    <div class='content'>
      <div class='budgetbg'>
        <Dropzone @filesDropped='upload'/>
        <transition name='fadein'>
          <BudgetMonth v-if='view=="month"' />
          <BudgetYear v-else-if='view=="year"' />
          <BudgetTrx v-else />
        </transition>
      </div>
      <Footer/>
    </div>
  </div>
</template>

<script>
  import * as _ from 'lodash';
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import BudgetMenu from './BudgetMenu';
  import BudgetMonth from './BudgetMonth';
  import BudgetYear from './BudgetYear';
  import BudgetTrx from './BudgetTrx';
  import Dropzone from '@/components/Dropzone';
  import Footer from '@/components/site/Footer';
  import Navigation from '@/components/site/Navigation';
  
  export default {
    name: 'Budget',
    components: {BudgetMenu, BudgetMonth, BudgetYear,
      BudgetTrx, Dropzone, Footer, Navigation},
    computed: {
      account: pathify.sync('budget/account'),
      accounts: pathify.sync('budget/accounts'),
      categories: pathify.sync('budget/categories'),
      demo: pathify.sync('budget/demo'),
      view: pathify.sync('budget/view'),
    },
    watch: {
      view: function(view) {
        utils.updateHistory(this.$router, {view});
      },
      account: function(account) {
        var accountid = account ? account.id : null;
        utils.updateHistory(this.$router, {account:accountid});
      },
    },

    // Mounted
    // Setup navigation, demo, accounts
    created: async function() {
      this.$store.set('global/layout', 'topnav');
      this.demo = Boolean(this.$route.query.demo);
      this.view = this.$route.query.view || 'month';
      // Fetch accounts and categories
      var apromise = api.Budget.getAccounts();
      var cpromise = api.Budget.getCategories();
      var {data:adata} = await apromise;
      var {data:cdata} = await cpromise;
      this.accounts = _.fromPairs(adata.results.map(x => [x.id, x]));
      this.categories = _.fromPairs(cdata.results.map(x => [x.id, x]));
      // Navigate to the account subtab
      var accountid = this.$route.query.account;
      if (accountid) { this.account = this.accounts[accountid]; }
    },
    
    methods: {
      // Upload
      // Upload dropped files
      upload: async function(formdata) {
        var {data} = await api.Budget.upload(formdata);
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
    user-select: none;
  }
  #budget.demo #sidebar .blur {
    color: transparent !important;
    text-shadow: 0 0 10px rgba($darkbg-text, 1) !important;
    user-select: none;
  }
</style>
