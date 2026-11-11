<template>
  <teleport to="body">
    <transition name='fade'>
      <div v-if='visible' :id='id' class='modal-overlay' @click.self='close'>
        <div class='modal-wrap' :class='`${theme}bg`'>
          <i v-if='closeButton' class='mdi mdi-close close-button' @click='emit("close")' />
          <div v-if='$slots.header' class='modal-header'><slot name='header'></slot></div>
          <div class='modal-content'><slot>modal-content</slot></div>
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
    id: {type:String},                              // Unique id for the modal
    visible: {type:Boolean, required:true},         // Display the modal
    closeButton: {type:Boolean, default:false},     // Display the close button
    closeOnEsc: {type:Boolean, default:false},      // Allow esc to close
    theme: {type:String, default:'light',           // Color theme: light or dark
      validator: value => ['light', 'dark'].includes(value)},
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
    align-items: center;
    background: #0006;
    display: flex;
    flex-direction: column;
    height: 100%;
    justify-content: flex-start;
    left: 0;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 99;

    .modal-wrap {
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      top: 15%;
      box-shadow: 0px 4px 8px #0008, 0px 8px 20px #0004;
      min-width: 500px;
      max-height: 80%;
      z-index: 100;

      .close-button {
        align-items: center;
        color: var(--fgcolor);
        display: flex;
        height: 32px;
        justify-content: center;
        position: absolute;
        right: 15px;
        top: 15px;
        width: 32px;
      }
      .modal-header {
        height: 70px;
        line-height: 70px;
        padding: 0px 20px;
        &>article { padding:0px; }
      }
      .modal-content {
        padding: 0px 20px 20px 20px;
        &>article { padding:0px; }
      }
      &:has(.modal-header) .modal-content {
        max-height: calc(100% - 70px);
        overflow-y: auto;
        overscroll-behavior: contain;
      }
      &:not(:has(.modal-header)) .modal-content {
        padding-top:20px;
      }
    }
  }

  /* Dark theme: darker shadow plus dark form inputs and buttons. Buttons use :where()
   * to keep specificity low so components like PillSelect can style their own. */
  .modal-wrap.darkbg {
    border: 1px solid #ffffff0d;
    box-shadow: 0px 6px 12px #000a, 0px 12px 40px #0008;
    label { color: var(--darkbg-fg4); }
    input, textarea, select {
      background-color: #fff1;
      border: 1px solid #fff1;
      box-shadow: none;
      color: var(--darkbg-fg1);
      &:focus { background-color: #fff1; box-shadow: var(--accent) 0px 0px 0px 1px; }
    }
    select option { background-color: var(--darkbg-bg0); color: var(--darkbg-fg1); }
    :where(button) {
      background-color: #fff2;
      color: var(--darkbg-fg2);
      &:where(:focus) { color: var(--darkbg-fg0); }
      &:where(:hover) { background-color: var(--darkbg-blue0); color: #fff; }
    }
  }
</style>
