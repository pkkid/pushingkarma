<template>
  <div id='newtab'>
    Hello NewTab!
  </div>
</template>

<script>
  export default {
    name: 'NewTab',
    mounted: function() {
      this.$store.set('global/layout', 'nonav');
    },
  };
</script>

<style lang='scss'>
  #newtab {
    background-color: black;
    height: 100vh;
    font-size: 1.6rem;
  }
</style>
