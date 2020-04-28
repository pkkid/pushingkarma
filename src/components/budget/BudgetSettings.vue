<template>
  <div id='budgetsettings'>
    <h1>
      Budget Settings
      <div class='subtext'>Edit budget accounts and categories</div>
    </h1>
    <b-tabs v-model='activetab' :animated='false'>
      <b-tab-item label='Bank Accounts'>
        <BudgetSettingsAccounts ref='0' class='fadein'/>
      </b-tab-item>
      <b-tab-item label='Categories'>
        <BudgetSettingsCategories ref='1' class='fadein'/>
      </b-tab-item>
    </b-tabs>
  </div>
</template>

<script>
  import * as utils from '@/utils/utils';
  import BudgetSettingsAccounts from './BudgetSettingsAccounts';
  import BudgetSettingsCategories from './BudgetSettingsCategories';

  export default {
    name: 'BudgetSettings',
    components: {BudgetSettingsAccounts, BudgetSettingsCategories},
    data: () => ({
      activetab: 0,
    }),
    mounted: function() {
      this.activetab = parseInt(this.$route.query.tab) || 0;
      this.$refs[0].$el.classList.add('showing');
    },
    watch: {
      // Watch Active Tab
      // When the tab changes, we mess with the class names to create the fadein
      // effect. We also update the tab argument in the URL parameters.
      activetab: async function(newtab, oldtab) {
        utils.updateHistory(this.$router, {tab:this.activetab});
        this.$refs[oldtab].$el.classList.remove('showing');
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
