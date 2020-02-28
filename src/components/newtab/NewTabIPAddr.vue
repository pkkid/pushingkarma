<template>
  <div id='ipaddr'>{{ipaddr}}</div>
</template>

<script>
  export default {
    name: 'NewTabIP',
    data: () => ({ipaddr: null}),
    mounted: function() {
      var globals = JSON.parse(document.getElementById('globals').textContent);
      this.ipaddr = globals.IPADDR;
    },
  };
</script>

<style lang='scss'>
  #ipaddr {
    background-color: $newtab_highlight;
    bottom: 2px;
    color: rgba(255,255,244,0.2);
    font-size: 12px;
    line-height: 12px;
    position: absolute;
    right: 5px;
    text-align: right;
    transition: $newtab_transition_slow;
    width: 150px;
  }
</style>
