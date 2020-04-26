<template>
  <div id='budgetsettings'>
    <h1>
      Budget Settings
      <div class='subtext'>Edit budget accounts and categories</div>
    </h1>
    <BudgetSettingsAccounts/>
  </div>
</template>

<script>
  import BudgetSettingsAccounts from './BudgetSettingsAccounts';

  export default {
    name: 'BudgetSettings',
    components: {BudgetSettingsAccounts},
  };
</script>
