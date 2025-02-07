<template>
  <Modal :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <div id='account'>
      <div class='loginform lightbg'>
        <h2>Login to PushingKarma</h2>
        <Quote style='margin-bottom:20px;'/>
        <label for='email'>Email</label>
        <input id='email' type='email'/>
        <label for='password'>Password</label>
        <input id='password' type='password'/>
      </div>
      <div class='image vignette'></div>
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
      display: flex;
      flex-direction: column;
    }
    .quote {
      font-style: italic;
      color: var(--dim);
      font-size: 13px;
      line-height: 1.5;
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

