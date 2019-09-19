<template>
  <portal to='modal-container'>
    <transition name='zoomfade' appear>
      <div class='modal'>
        <div class='modal-overlay' @click='bgClose && $emit("close")'></div>
        <div class='modal-wrapper'>
          <div class='modal-container zoom' :style='{width,height,padding}'>
            <div class='modal-body'><slot name='body'>Default Body</slot></div>
            <div class='modal-close' v-if='xClose' @click='$emit("close")'>×</div>
          </div>
        </div>
      </div>
    </transition>
  </portal>
</template>

<script>
  export default {
    name: 'Modal',
    props: {
      height: {default: null},
      width: {default: '300px'},
      padding: {default: '20px 30px'},
      bgClose: {default: false},
      escClose: {default: false},
      xClose: {default: true},
    },
    methods: {
      /** Check to close the model when pressing esc. **/
      keyClose: function(event) {
        if (event.keyCode === 27) { this.$emit('close'); }
      }
    },

    /** Start listening to keyup events. */
    mounted: function() {
      document.body.classList.add('modalOpen');
      if (this.escClose) { document.addEventListener('keyup', this.keyClose); }
    },

    /** Stop listening to keyup events. */
    beforeDestroy: function() {
      document.body.classList.remove('modalOpen');
      if (this.escClose) { document.removeEventListener('keyup', this.keyClose); }
    },
  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  .modal {
    z-index: 98;
  }
  .modal,
  .modal-overlay {
    display: table;
    height: 100%;
    position: fixed;
    left: 0;
    top: 0;
    transition: opacity .3s ease;
    width: 100%;
  }
  .modal-overlay {
    background-color: rgba(0, 0, 0, .2);
  }
  .modal-wrapper {
    display: table-cell;
    vertical-align: middle;
  }
  .modal-container {
    background-color: $content-bg;
    border-radius: 8px;
    box-shadow: 0 2px 20px rgba(0, 0, 0, .8);
    color: $dark-bg0;
    margin: 0px auto;
    position: relative;
    transition: all .3s ease;
    width: 400px;
  }
  .modal-close {
    position: absolute;
    top: -4px;
    right: 5px;
    color: $content-bg;
    font-size: 40px;
    cursor: pointer;
  }
  
  // .modal-enter { opacity:0; }
  // .modal-enter-active { transition: all .3s ease; }
  // .modal-leave-active { opacity:0; }
  // .modal-enter .modal-container,
  // .modal-leave-active .modal-container { transform: scale(1.1); }
</style>
