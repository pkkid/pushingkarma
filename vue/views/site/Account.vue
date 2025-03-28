<template>
  <Modal id='account-modal' :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <div id='account'>
      <div class='content lightbg'>
        
        <!-- Login Form -->
        <form v-if='!user' class='loginform' @submit.prevent='login'>
          <h2>Login to PushingKarma</h2>
          <Quote style='margin-bottom:10px;'/>
          <label for='email'>Email</label>
          <input id='email' type='email' v-model='email'/>
          <label for='password'>Password</label>
          <input id='password' type='password' v-model='password'/>
          <button type='submit' style='margin-top:20px;'>Login</button>
        </form>
        
        <!-- Current User Data -->
        <div v-else class='lightbg'>
          <h2>Welcome {{user.name}}!</h2>
          <Quote style='margin-bottom:10px;'/>
          <dl style='grid-template-columns: 70px 230px;'>
            <dt>Joined</dt><dd>{{utils.formatDate(user.date_joined, 'MMM D, YYYY')}}</dd>
            <dt>Login</dt><dd>{{utils.timeAgo(user.last_login)}}</dd>
            <dt>Email</dt><dd>{{user.email}}</dd>
            <dt>Apikey</dt><dd>{{user.auth_token}}
              <div style='font-size:10px'>
                <a @click.prevent @click='genToken' style='margin-right:5px'>Regenerate</a>&nbsp;
                <a @click.prevent @click='copyToken'>Copy</a>
              </div>
            </dd>
          </dl>
          <button style='margin-top:20px;' @click='logout'>Logout</button>
        </div>

      </div>
      <div class='image vignette'></div>
    </div>
  </Modal>
</template>

<script setup>
  import {inject, ref} from 'vue'
  import {Modal, Quote} from '@/components'
  import {api, utils} from '@/utils'

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
      console.log(`Logged in as ${user.value.email}`)
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

  // Generate Token
  // Create a new API token for the current user
  const genToken = async function(event) {
    utils.animate(event.target, 'rotate-bounce', 500)
    var {data} = await api.Main.generateToken()
    setUser(data)
  }

  // Copy Token
  // Copy the token to the clipboard
  const copyToken = async function(event) {
    utils.animate(event.target, 'rotate-bounce', 500)
    utils.copyText(user.value.auth_token)
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
      background-image: url('/static/img/mtn-field.png');
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

