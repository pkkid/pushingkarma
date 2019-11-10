<template>
  <transition name='custom-classes-transition'
      enter-active-class='animated flipInX'
      leave-active-class='animated fadeOutUp'>
    <div id='notification' v-if='message'>
      <i class='mdi' :class='icon'/> {{message}}
    </div>
  </transition>
</template>

<script>
  export default {
    name: 'Notification',
    data: () => ({
      message: '',
      icon: 'mdi-check',
      timeout: 5000,
    }),
    mounted: function() {
      var self = this;
      this.$root.$on('notify', function(message, icon) {
        console.log(message);
        self.message = message;
        self.icon = icon;
        setTimeout(() => self.message='', self.timeout);
      });
    },
  };
</script>

<style lang='scss'>
  #notification {
    animation-duration: 0.6s;
    background-color: #111;
    border-radius: 4px;
    box-shadow: 0 2px 3px rgba(0, 0, 0, .5);
    font-size: 1.5rem;
    font-weight: 500;
    line-height: 1.5em;
    max-width: 300px;
    padding: 8px 20px 10px 15px;
    position: fixed;
    right: 20px;
    top: 80px;
    z-index: 101;
    .mdi {
      font-size: 1.5em;
      margin-right: 5px;
      position: relative;
      top: 3px;
    }
  }
</style>
