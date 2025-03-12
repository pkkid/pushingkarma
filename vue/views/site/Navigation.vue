<template>
  <div id='navigation' class='darkbg'>
    <Logo @dblclick='showAccount=true'/>
    <Account :visible='showAccount' @close='showAccount=false'/>
    <div class='sitelinks'>
      <div><router-link to='/#splash'>Home</router-link></div>
      <div><router-link to='/#projects'>Projects</router-link></div>
      <div><router-link to='/notes'>Notes</router-link></div>
      <div v-if='user?.id'><router-link to='/budget'>Budget</router-link></div>
      <div v-if='user?.id'><a href='#' @click.prevent @click='showAccount=true'>{{user.name}}</a></div>
      <div v-if='user?.id'><a :href='apiurl' target='_blank'>API</a></div>
    </div>
  </div>
</template>

<script setup>
  import {inject, ref} from 'vue'
  import Logo from '@/views/site/Logo.vue'
  import Account from '@/views/site/Account.vue'

  const {user} = inject('user')
  const {apiurl} = inject('apiurl')
  const showAccount = ref(false)
</script>

<style>
  /* Base Navigation Styles */
  #navigation {
    .sitelinks {
      display: flex;
      flex-wrap: nowrap;
      justify-content: space-between;
      a {
        font-weight: 400;
        letter-spacing: 1px;
        position: relative;
        text-decoration: none;
        text-transform: uppercase;
      }
      a:before {
        background-color: var(--darkbg-bg0);
        content: "";
        height: 2px;
        left: 100%;
        margin-left: 10px;
        position: absolute;
        top: calc(50% - 0px);
        transform: translateY(-50%);
        transition: all .3s ease;
        width: 0px;
      }
      a:hover:before {
        width: 35px;
        background-color: var(--accent);
      }
    }
  }

  /* Left Navigation */
  body.leftnav {
    --navwidth: 300px;
    --navheight: 0px;
    #navigation {
      height: 100vh;
      position: fixed;
      width: var(--navwidth);
      .sitelinks {
        margin-top: 250px;
        margin-left: 66px;
        flex-direction: column;
        div { padding-bottom: 15px; }
      }
    }
    #content {
      padding-left: var(--navwidth);
    }
  }

  /* Top Navigation */
  body.topnav {
    --navwidth: 0px;
    --navheight: 60px;
    #navigation {
      height: 60px;
      line-height: var(--navheight);
      box-shadow: 0px 1px 2px #0003;
      position: fixed;
      width: 100vw;
      z-index: 99;
      .sitelinks {
        width: 450px;
        margin-left: 320px;
        justify-content: flex-start;
        & > div { padding-right: 70px; }
      }
    }
    #content {
      padding-top: var(--navheight);
    }
  }

</style>
