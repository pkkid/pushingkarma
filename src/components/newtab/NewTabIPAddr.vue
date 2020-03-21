<template>
  <div id='ipaddr'>{{globals.IPADDR}}</div>
</template>

<script>
  import * as pathify from 'vuex-pathify';

  export default {
    name: 'NewTabIP',
    computed: {
      globals: pathify.get('global/globals'),
    },
  };
</script>

<style lang='scss'>
  #ipaddr {
    bottom: 2px;
    color: rgba(255,255,244,0.2);
    font-size: 12px;
    line-height: 12px;
    position: absolute;
    right: 5px;
    text-align: right;
    transition: $newtab_transition_fast;
    width: 150px;
  }
</style>
