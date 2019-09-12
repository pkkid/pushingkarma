<template>
  <portal to='modal-container'>
    <transition name='modal' :appear='true'>
      <div class='modal-overlay'>
        <div class='modal-wrapper'>
          <div class='modal-container'>
            <div class='modal-body'><slot name='body'>default body</slot></div>
            <div class='modal-footer'>
              <slot name='footer'>
                <button class='modal-default-button' @click='$emit("close")'>OK</button>
                <div style='clear:both'></div>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </portal>
</template>

<script>
  export default {
    name:'Modal',
  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  .modal-overlay {
    background-color: rgba(0, 0, 0, .5);
    display: table;
    height: 100%;
    position: fixed;
    left: 0;
    top: 0;
    transition: opacity .3s ease;
    width: 100%;
    z-index: 98;
  }
  .modal-container {
    background-color: #eee;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
    color: $dark-bg0;
    margin: 0px auto;
    padding: 20px 30px;
    transition: all .3s ease;
    width: 400px;
  }
  .modal-wrapper { display:table-cell; vertical-align:middle; }
  .modal-body { margin-bottom:20px; }
  .modal-default-button { float:right; }
  
  .modal-enter { opacity:0; }
  .modal-enter-active { transition: all .3s ease; }
  .modal-leave-active { opacity:0; }
  .modal-enter .modal-container,
  .modal-leave-active .modal-container { transform: scale(1.1); }
</style>
