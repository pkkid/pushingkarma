<template>
  <teleport to="body">
    <transition name='fade'>
      <div v-if='visible' class='modal-overlay' @click.self='close'>
        <div class='modal-content'>
          <i v-if='closeButton' class='mdi mdi-close' @click='emit("close")' />
          <slot>modal-content</slot>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
  import {onMounted, onBeforeUnmount, watchEffect} from 'vue'
  import hotkeys from 'hotkeys-js'

  var prevScope = null                              // Previous hotkeys-js scope
  const emit = defineEmits(['close'])               // Emit when closing the modal
  const props = defineProps({
    visible: {type:Boolean, required:true},         // Display the modal
    closeButton: {type:Boolean, default:false},     // Display the close button
    closeOnEsc: {type:Boolean, default:false}       // Allow esc to close
  })

  // Watch visible
  // Sets the hotkeys-js scope
  watchEffect(function() {
    if (props.visible) {
      prevScope = hotkeys.getScope()
      hotkeys.setScope('modal')
    } else {
      hotkeys.setScope(prevScope)
    }
  })

  // On Mounted
  // watch for esc pressed
  onMounted(function() {
    if (props.closeOnEsc) {
      hotkeys('esc', 'modal', function() { emit('close') })
    }
  })

  // On Before Unmount
  // stop watching hotkeys
  onBeforeUnmount(function() {
    hotkeys.deleteScope('modal')
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
    justify-content: flex-start;
    flex-direction: column;
    align-items: center;
    z-index: 1000;
    .modal-content {
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      top: 15%;
      box-shadow: 0px 4px 8px #0008, 0px 8px 20px #0004;
      min-width: 500px;
    }
    .mdi-close {
      color: var(--lightbg-fg1);
      position: absolute;
      right: 15px;
      top: 15px;
      width: 32px;
      height: 32px;
      display: flex;
      justify-content: center;
      align-items: center;
    }
  }
</style>
