<template>
  <div id='budget' :class={demo}>
    <Navigation :cls="'topnav'" />
    <BudgetAccounts/>
    <div class='content'>
      <div class='budgetbg'>
        <Dropzone @filesDropped='upload'/>
        <transition name='fadein'>
          <BudgetMonth v-if='view=="budget"' />
          <BudgetTransactions v-else />
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
  import BudgetAccounts from './BudgetAccounts';
  import BudgetMonth from './BudgetMonth';
  import BudgetTransactions from './BudgetTransactions';
  import Dropzone from '@/components/Dropzone';
  import Footer from '@/components/site/Footer';
  import Navigation from '@/components/site/Navigation';
  
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
    computed: {
      accounts: pathify.sync('budget/accounts'),
      categories: pathify.sync('budget/categories'),
      demo: pathify.sync('budget/demo'),
      transactions: pathify.sync('budget/transactions'),
      view: pathify.sync('budget/view'),
    },

    // Mounted
    // Setup navigation, demo, accounts
    mounted: async function() {
      this.$store.set('global/layout', 'topnav');
      this.demo = Boolean(this.$route.query.demo);
      var apromise = api.Budget.getAccounts();
      var cpromise = api.Budget.getCategories();
      var {data:adata} = await apromise;
      var {data:cdata} = await cpromise;
      this.accounts = _.fromPairs(adata.results.map(x => [x.id, x]));
      this.categories = _.fromPairs(cdata.results.map(x => [x.id, x]));
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
