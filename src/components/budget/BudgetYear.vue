<template>
  <div id='budgetmonth'>
    <h3>Past Year Budget</h3>
    <div class='tablewrap'>
      Hi Dad!
    </div>
  </div>
</template>

<script>
  export default {
    name: 'BudgetYear',
  };
</script>

<style lang='scss'>
  #budgetmonth {
    padding: 10px 20px;

    .tablewrap {
      background-color: white;
      border: 1px solid darken($lightbg-color, 20%);
      border-radius: 2px;
      box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
      padding: 20px 10px;
      min-width: 1000px;
    }

  }
</style>
