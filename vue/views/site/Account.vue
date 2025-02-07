<template>
  <Modal :visible='visible' @close='emit("close")'>
    <div id='account'>
      <div class='loginform'>
        <h2>Login to PushingKarma</h2>
        <Quote/>
      </div>
      <div class='image vignette'>
      </div>
    </div>
  </Modal>
</template>

<script setup>
  import {ref} from 'vue'
  import {defineProps, defineEmits} from 'vue'
  import Modal from '@/components/Modal.vue'
  import Quote from '@/components/Quote.vue'

  const emit = defineEmits(['close'])
  const props = defineProps({
    visible: {type:Boolean, required:true},
  })
</script>

<style>
  #account {
    display: flex;
    flex-direction: row;

    .loginform {
      width: 350px;
      padding: 20px;
    }
    .quote {
      font-style: italic;
      color: var(--dim);
      font-size: 13px;
      line-height: normal;
    }

    .image {
      background-image: url('/static/img/mtn-field.png');
      background-position: center center;
      background-size: cover;
      border-bottom-right-radius: 8px;
      border-top-right-radius: 8px;
      width: 400px; height: 400px;
    }
   

  }
</style>

