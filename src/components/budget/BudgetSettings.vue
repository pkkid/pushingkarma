<template>
  <div id='budgetsettings'>
    <PageWrap>
      <h1>
        Budget Settings
        <div class='subtext'>Edit budget accounts and categories</div>
      </h1>
      <b-tabs v-model='activetab' :animated='false' destroy-on-hide>
        <b-tab-item label='Bank Accounts'>
          <BudgetAccounts ref='0' class='fadein'/>
        </b-tab-item>
        <b-tab-item label='Categories'>
          <BudgetCategories ref='1' class='fadein'/>
        </b-tab-item>
      </b-tabs>
    </PageWrap>
  </div>
</template>

<script>
  import * as utils from '@/utils/utils';
  import BudgetAccounts from './BudgetAccounts';
  import BudgetCategories from './BudgetCategories';
  import PageWrap from '@/components/site/PageWrap';

  export default {
    name: 'BudgetSettings',
    components: {PageWrap, BudgetAccounts, BudgetCategories},
    data: () => ({
      activetab: null,
    }),
    mounted: async function() {
      this.activetab = parseInt(this.$route.query.tab) || 0;
    },
    watch: {
      // Watch Active Tab
      // When the tab changes, we mess with the class names to create the fadein
      // effect. We also update the tab argument in the URL parameters.
      activetab: async function(newtab, oldtab) {
        utils.updateHistory(this.$router, {tab:this.activetab});
        if (this.$refs[oldtab] !== undefined) {
          this.$refs[oldtab].$el.classList.remove('showing');
        }
        await utils.sleep(100);
        this.$refs[newtab].$el.classList.add('showing');
      },
    }
  };
</script>

<style lang='scss'>
  .fadein {
    opacity: 0;
    transition: opacity 0.5s ease;
    &.showing { opacity: 1; }
  }
</style>
