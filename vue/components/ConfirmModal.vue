<template>
  <Modal :id='id' :visible='visible' :theme='theme' closeButton @close='emit("cancel")'>
    <div class='confirm' tabindex='-1' @keydown.esc.stop.prevent='emit("cancel")'>
      <h2>{{title}}</h2>
      <p>{{message}}</p>
      <div class='buttons'>
        <button ref='confirmEl' type='button' :class='{danger}' @click='emit("confirm")'>{{confirmLabel}}</button>
        <button type='button' @click='emit("cancel")'>Cancel</button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
  // Confirm Modal
  // Ask the user to confirm an action using the site modal. Emits confirm or
  // cancel; the parent controls visibility. The confirm button is focused when
  // opened so enter confirms and escape cancels. Escape is handled here and
  // stopped so it doesn't also reach page level key handlers behind the modal.
  import {nextTick, ref, watch} from 'vue'
  import Modal from './Modal.vue'

  const emit = defineEmits(['confirm', 'cancel'])
  const confirmEl = ref(null)                       // Confirm button, focused when opened
  const props = defineProps({
    id: {type:String, default:'confirm-modal'},     // Unique id for the modal
    visible: {type:Boolean, required:true},         // Display the modal
    title: {type:String, default:'Are you sure?'},  // Heading text
    message: {type:String, default:''},             // Question or details to display
    confirmLabel: {type:String, default:'OK'},      // Confirm button text
    danger: {type:Boolean, default:false},          // Style the confirm button as destructive
    theme: {type:String, default:'light'},          // Modal theme: light or dark
  })

  // Watch Visible
  // Focus the confirm button when opened
  watch(() => props.visible, async function(visible) {
    if (!visible) { return }
    await nextTick()
    confirmEl.value?.focus()
  })
</script>

<style>
  .modal-wrap:has(> .modal-content > .confirm) { max-width: 460px; min-width: 380px; }
  .confirm {
    outline: none;
    h2 { margin-top: 0px; }
    p { line-height: 1.5; margin: 0px; }
    .buttons { display: flex; gap: 8px; margin-top: 20px; }
    button.danger:hover { background-color: var(--lightbg-red0); color: #fff; }
  }
</style>
