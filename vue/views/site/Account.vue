<template>
  <Modal id='account-modal' :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <div id='account'>
      <div class='content lightbg'>
        
        <!-- Login Form (name and autocomplete attributes let password managers fill it) -->
        <form v-if='!user' class='loginform' @submit.prevent='login'>
          <h2>Login to PushingKarma</h2>
          <Quote style='margin-bottom:10px;'/>
          <label for='email'>Email</label>
          <input id='email' ref='emailEl' name='email' type='email' autocomplete='username' v-model='email'/>
          <label for='password'>Password</label>
          <input id='password' name='password' type='password' autocomplete='current-password' v-model='password'/>
          <button type='submit' style='margin-top:20px;'>Login</button>
        </form>
        
        <!-- Current User Data -->
        <div v-else class='lightbg'>
          <h2>Welcome {{user.first_name}}!</h2>
          <Quote style='margin-bottom:10px;'/>
          <dl style='grid-template-columns: 70px 230px;'>
            <dt>Joined</dt><dd>{{utils.formatDate(user.date_joined, 'MMM D, YYYY')}}</dd>
            <dt>Login</dt><dd>{{utils.timeAgo(user.last_login ? new Date(user.last_login).getTime() : null)}}</dd>
            <dt>Email</dt><dd>{{user.email}}</dd>
          </dl>
          <button style='margin-top:20px;' @click='logout'>Logout</button>
        </div>

      </div>
      <div class='image vignette'></div>
    </div>
  </Modal>
</template>

<script setup>
  import {inject, nextTick, ref, watch} from 'vue'
  import {Modal, Quote} from '@/components'
  import {api, utils} from '@/utils'

  const {user, setUser} = inject('user')
  const emit = defineEmits(['close'])
  const email = ref('')
  const password = ref('')
  const emailEl = ref(null)                         // Email input, focused when the login form opens
  const props = defineProps({
    visible: {type:Boolean, required:true},
  })

  // Watch Visible
  // Focus the email input when the login form is opened
  watch(() => props.visible, async function(visible) {
    if (!visible || user.value) { return }
    await nextTick()
    emailEl.value?.focus()
  })

  // Login
  // Login using username/password
  const login = async function() {
    var params = {email:email.value, password:password.value}
    var {data} = await api.Main.login(params)
    if (data.id) {
      setUser(data)
      console.info(`Logged in as ${user.value.email}`)
    }
  }

  // Logout
  // Log out of the current session
  const logout = async function() {
    await api.Main.logout()
    setUser(null)
    email.value = ''
    password.value = ''
  }
</script>

<style>
  #account {
    display: flex;
    flex-direction: row;
    .content > * {
      width: 350px;
      padding: 0px 20px 0px 0px;
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
      background-image: url('/static/img/backgrounds/ai-2025-mtnfield.png');
      background-position: center center;
      background-size: cover;
      border-bottom-right-radius: 8px;
      border-top-right-radius: 8px;
      height: 400px;
      margin: -20px -20px -20px 0px;
      width: 400px;
    }
    a { display: inline-block; }
  }
  #account-modal .modal-wrap {
    min-height: 340px !important;
    .modal-content { overflow: hidden; }
  }
</style>

