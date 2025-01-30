<template>
  <transition name='modal-fade'>
    <div v-if='visible' class='modal-overlay' @click.self='close'>
      <div class='modal-content'>
        <button v-if='showCloseButton' class='modal-close-button' @click='close'>X</button>
        <slot></slot>
      </div>
    </div>
  </transition>
</template>

<script setup>
  import {onMounted, onBeforeUnmount} from 'vue'
  import {defineProps, defineEmits} from 'vue'

  const props = defineProps({
    visible: {type:Boolean, required:true},
    showCloseButton: {type:Boolean, default:true},
    closeOnEsc: {type:Boolean, default:true}
  })

  const emit = defineEmits(['update:visible'])
  const close = function() {
    emit('update:visible', false)
  }
  const handleEsc = function(event) {
    if (props.closeOnEsc && event.key === 'Escape') { close() }
  }
  onMounted(function() {
    if (props.closeOnEsc) {
      document.addEventListener('keydown', handleEsc)
    }
  })
  onBeforeUnmount(function() {
    if (props.closeOnEsc) {
      document.removeEventListener('keydown', handleEsc)
    }
  })
</script>

<style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000; /* Ensure the modal is on top */
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .modal-content {
    background: white;
    padding: 20px;
    border-radius: 5px;
    position: relative;
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

  .modal-fade-enter-active,
  .modal-fade-leave-active {
    transition: opacity 0.3s ease;
  }
  .modal-fade-enter-from,
  .modal-fade-leave-to {
    opacity: 0;
  }
</style>