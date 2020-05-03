<template>
  <div id='budget' :class={demo}>
    <Navigation :cls="'topnav'"/>
    <SidePanel>
      <template v-slot:sidepanel>
        <BudgetMenu/>
      </template>
      <template v-slot:contentarea>
        <Dropzone @filesDropped='upload'>
          <PageWrap>
            <transition name='fadein'>
              <BudgetMonth v-if='view=="month"'/>
              <BudgetYear v-else-if='view=="year"'/>
              <BudgetSettings v-else-if='view=="settings"'/>
              <BudgetTransactions v-else/>
            </transition>
          </PageWrap>
        </Dropzone>
      </template>
    </SidePanel>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as pathify from 'vuex-pathify';
  import * as utils from '@/utils/utils';
  import BudgetMenu from './BudgetMenu';
  import BudgetMonth from './BudgetMonth';
  import BudgetSettings from './BudgetSettings';
  import BudgetYear from './BudgetYear';
  import BudgetTransactions from './BudgetTransactions';
  import SidePanel from '@/components/site/SidePanel';
  import PageWrap from '@/components/site/PageWrap';
  import Dropzone from '@/components/Dropzone';
  import Navigation from '@/components/site/Navigation';
  
  export default {
    name: 'Budget',
    components: {BudgetMenu, BudgetMonth, BudgetYear, BudgetSettings,
      BudgetTransactions, Dropzone, Navigation, SidePanel, PageWrap},
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
        window.scrollTo(0,0);
      },
      account: function(account) {
        var accountid = account ? account.id : null;
        utils.updateHistory(this.$router, {account:accountid});
        window.scrollTo(0,0);
      },
    },

    // Mounted
    // Setup navigation, demo, accounts
    created: async function() {
      this.demo = Boolean(this.$route.query.demo);
      this.view = this.$route.query.view || 'month';
      // Fetch accounts and categories
      var apromise = api.Budget.getAccounts();
      var cpromise = api.Budget.getCategories();
      var {data:adata} = await apromise;
      var {data:cdata} = await cpromise;
      this.accounts = adata.results;
      this.categories = cdata.results;
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
  #budget {
    // Tweak page style and article styles
    #pagewrap { padding:30px 30px 60px 30px; }
    #page { margin:0px auto; padding:25px 30px; max-width:1000px; min-width:800px; }
    p { margin-top:0px; width:85%; }
  }

  // Demo mode blurs all financial values
  .demo .blur,
  .demo #sidepanel .blur {
    color: transparent !important;
    text-shadow: 0 0 10px rgba($lightbg-fg0, 0.6) !important;
    user-select: none;
  }
  .demo #sidepanel .blur {
    text-shadow: 0 0 10px rgba($darkbg-fg0, 0.6) !important;
  }
</style>
