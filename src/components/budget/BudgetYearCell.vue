<template>
  <div :class='{blur:cat.name == "Income"}'>{{spent | usdint(0)}}</div>
</template>

<script>
  import * as _ from 'lodash';

  export default {
    name: 'BudgetYearCell',
    props: {
      groups: {default: {}},     // Categopry groups
      cat: {default: {}},        // Category
      monthstr: {default: ''},   // Month string
    },
    computed: {
      trxs: function() { return this.groups[this.cat.name][this.monthstr]; },
      spent: function() {
        return _.sum(_.map(this.trxs, (x) => parseFloat(x.amount)));
      },
    },
  };
</script>

<style lang='scss'>

</style>
