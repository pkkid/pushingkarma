<template>
  <div id='navigation' class='darkbg'>
    <Logo @dblclick='showAccount=true'/>
    <Account :visible='showAccount' @close='showAccount=false'/>
    <div class='sitelinks'>
      <div><router-link to='/#splash'>Home</router-link></div>
      <div><router-link to='/#projects'>Projects</router-link></div>
      <div><router-link to='/notes'>Notes</router-link></div>
      <div><router-link to='/budget'>Budget</router-link></div>
    </div>
  </div>
</template>

<script setup>
  import {ref} from 'vue'
  import Logo from '@/views/site/Logo.vue'
  import Account from '@/views/site/Account.vue'

  const showAccount = ref(false)
</script>

<style>
  /* Base Navigation Styles */
  #navigation {
    position: fixed;
    font-family: 'Merriweather';
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
    #navigation {
      width: var(--navwidth);
      height: 100vh;
      .sitelinks {
        margin-top: 250px;
        margin-left: 66px;
        flex-direction: column;
        div { padding-bottom: 15px; }
      }
    }
  }

  /* Top Navigation */
  body.topnav {
    #navigation {
      line-height: var(--navheight);
      width: 100vw;
      height: 60px;
      z-index: 99;
      .sitelinks {
        width: 450px;
        margin-left: 320px;
      }
    }
  }

</style>
