<template>
  <i class='mdi' :class='[icon, animation, {"animated":animated}]' @click='animate'/>
</template>

<script>
  export default {
    name: 'IconButton',
    props: {
      icon: {default: 'mdi-refresh'},
      animation: {default: 'btnzoom'},
      click: {default: null},
    },
    data: () => ({
      animated: false
    }),
    methods: {
      animate() {
        var self = this;
        this.animated = true;
        setTimeout(function() {
          self.animated=false;
          if (self.click) { self.click(); }
        }, 1000);
      }
    }
  };
</script>

<style lang='scss'>
  i.btnzoom {
    display: block;
    float: right;
    font-size: 1.1em;
  }
  i.btnzoom.animated {
    transition: all .5s;
    transform: scale(1.5);
    opacity: 0;
  }
</style>
