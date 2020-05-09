<template>
  <div id='budgetmonth'>
    <PageWrap>
      <h1>January Budget</h1>
      Hi Mom!
    </PageWrap>
  </div>
</template>

<script>
  import PageWrap from '@/components/site/PageWrap';

  export default {
    name: 'BudgetMonth',
    components: {PageWrap},
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .tablewrap {
      background-color: white;
      border: 1px solid darken($lightbg-bg3, 10%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 10px;
      min-width: 1000px;
    }

  }
</style>
