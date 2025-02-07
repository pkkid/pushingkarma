<template>
  <teleport to="body">
    <transition name='modal-fade'>
      <div v-if='visible' class='modal-overlay' @click.self='close'>
        <div class='modal-content lightbg'>
          <!-- <button v-if='showCloseButton' class='modal-close-button' @click='emit("close")'>x</button> -->
          <slot>modal-content</slot>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
  import {onMounted, onBeforeUnmount} from 'vue'
  import {defineProps, defineEmits} from 'vue'

  const props = defineProps({
    visible: {type:Boolean, required:true},
    showCloseButton: {type:Boolean, default:true},
    closeOnEsc: {type:Boolean, default:true}
  })

  const emit = defineEmits(['close'])
</script>

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #0006;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  .modal-content {
    border-radius: 8px;
    position: relative;
    top: -10%;
    box-shadow: 0px 4px 8px #0008, 0px 8px 20px #0004;
    min-width: 500px;
    min-height: 200px;
  }
  .modal-close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: transparent;
    border: none;
    font-size: 20px;
    cursor: pointer;
  }

  /* Fade Transition */
  .modal-fade-enter-active,
  .modal-fade-leave-active {
    transition: opacity 0.3s ease;
  }
  .modal-fade-enter-from,
  .modal-fade-leave-to {
    opacity: 0;
  }
</style>