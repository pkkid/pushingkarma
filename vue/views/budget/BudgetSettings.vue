<template>
  <Modal :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <div id='budgetsettings' class='lightbg'>
      <h2>Budget Settings</h2>
      <div class='accounts'>
        <h3>Accounts</h3>
      </div>
    </div>
  </Modal>
</template>

<script setup>
  import Modal from '@/components/Modal.vue'

  const emit = defineEmits(['close'])
  const props = defineProps({
    visible: {type:Boolean, required:true},
  })

</script>

<style>
  #budgetsettings {
    padding: 20px;
    width: 600px;
  }
</style>
