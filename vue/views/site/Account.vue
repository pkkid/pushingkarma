<template>
  <Modal :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <div id='account'>
      <div class='content lightbg'>
        <form v-if='!user?.id' class='loginform' @submit.prevent="login()">
          <h2>Login to PushingKarma</h2>
          <Quote style='margin-bottom:10px;'/>
          <label for='email'>Email</label>
          <input id='email' type='email' v-model='email'/>
          <label for='password'>Password</label>
          <input id='password' type='password' v-model='password'/>
          <button type='submit' style='margin-top:20px;'>Login</button>
        </form>
        <div v-else class='lightbg'>
          <h2>Welcome {{user.name}}!</h2>
          <Quote style='margin-bottom:10px;'/>
          Joined --<br/>
          Login --<br/>
          Email --<br/>
          Apikey --<br/>
          Regenerate - Copy<br/>
        </div>
      </div>
      <div class='image vignette'></div>
    </div>
    
  </Modal>
</template>

<script setup>
  import {inject, ref} from 'vue'
  import {api} from '@/utils'
  import Modal from '@/components/Modal.vue'
  import Quote from '@/components/Quote.vue'

  const {user, setUser} = inject('user')

  const emit = defineEmits(['close'])
  const email = ref('')
  const password = ref('')
  const props = defineProps({
    visible: {type:Boolean, required:true},
  })

  // Login
  // Login using username/password
  const login = async function() {
    var params = {email:email.value, password:password.value}
    var {data} = await api.Main.login(params)
    if (data.id) {
      setUser(data)
      email.value = ''
      password.value = ''
      console.log(`Logged in as ${user.value.email}`)
    }
  }
</script>

<style>
  #account {
    display: flex;
    flex-direction: row;
    .content > * {
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

