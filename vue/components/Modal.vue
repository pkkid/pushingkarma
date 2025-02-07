<template>
  <teleport to="body">
    <transition name='modal-fade'>
      <div v-if='visible' class='modal-overlay' @click.self='close'>
        <div class='modal-content'>
          <span v-if='closeButton' class='icon modal-close-button' @click='emit("close")'>close</span>
          <slot>modal-content</slot>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
  import {onMounted, onBeforeUnmount} from 'vue'
  import {defineProps, defineEmits} from 'vue'
  import hotkeys from 'hotkeys-js'

  const emit = defineEmits(['close'])
  const props = defineProps({
    visible: {type:Boolean, required:true},
    closeButton: {type:Boolean, default:false},
    closeOnEsc: {type:Boolean, default:false}
  })

  // On Mounted
  // watch for esc pressed
  onMounted(function() {
    if (props.closeOnEsc) {
      hotkeys('esc', function() {  emit('close') })
    }
  })

  // On Before Unmount
  // stop watching hotkeys
  onBeforeUnmount(function() {
    hotkeys.unbind('esc')
  })
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
    overflow: hidden;
    position: relative;
    top: -10%;
    box-shadow: 0px 4px 8px #0008, 0px 8px 20px #0004;
    min-width: 500px;
    min-height: 200px;
  }
  .modal-close-button {
    background: transparent;
    border-radius: 50%;
    border: none;
    color: var(--lightbg-fg1);
    cursor: pointer;
    font-size: 20px;
    opacity: 0.7;
    padding: 5px;
    position: absolute;
    top: 15px; right: 15px;
    transition: all 0.2s ease;
    z-index: 1001;
    &:hover {
      opacity: 1;
      background-color: #0001;
    }
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