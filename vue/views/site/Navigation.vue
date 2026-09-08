<template>
  <nav id='navigation' class='darkbg' :class='{"menu-open":menuOpen}' @keydown.esc='closeMenu'>
    <Logo @dblclick='openAccount'/>
    <Account :visible='showAccount' @close='showAccount=false'/>
    <button ref='menuToggle' class='menu-toggle' type='button' :title='menuOpen ? "Close menu" : "Menu"' @click='menuOpen=!menuOpen'>
      <i class='mdi' :class='menuOpen ? "mdi-close" : "mdi-menu"'/>
    </button>
    <div class='sitelinks' @click='menuOpen=false'>
      <div class='home'><router-link to='/#splash'>Home</router-link></div>
      <div class='projects' v-if='!user?.id'><router-link to='/#projects'>Projects</router-link></div>
      <div class='notes'><router-link to='/notes'>Notes</router-link></div>
      <div class='budget' v-if='user?.id'><router-link to='/budget'>Budget</router-link></div>
      <div class='stocks' v-if='user?.id'><router-link to='/stocks'>Stocks</router-link></div>
      <div class='account' v-if='user?.id'><button type='button' @click='openAccount'>{{user.first_name || 'Account'}}</button></div>
      <div class='apidoc' v-if='user?.id'><a href='/apidoc'>API</a></div>
    </div>
  </nav>
</template>

<script setup>
  import {inject, ref, watch} from 'vue'
  import {useRoute} from 'vue-router'
  import {Account, Logo} from '@/views/site'

  const {user} = inject('user')
  const route = useRoute()
  const showAccount = ref(false)
  const menuOpen = ref(false)
  const menuToggle = ref(null)

  // Watch Route
  // Close the mobile menu when the route changes
  watch(() => route.fullPath, function() { menuOpen.value = false })

  // Close Menu
  // Close the mobile menu and return focus to the toggle button
  function closeMenu() {
    if (menuOpen.value) {
      menuOpen.value = false
      menuToggle.value?.focus()
    }
  }

  // Open Account
  // Close the mobile menu and show the account dialog
  function openAccount() {
    menuOpen.value = false
    showAccount.value = true
  }
</script>

<style>
  /* Base Navigation Styles */
  #navigation {
    top: 0;
    left: 0;
    .menu-toggle { display: none; }
    a:focus-visible, button:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 3px;
    }
    .sitelinks {
      display: flex;
      flex-wrap: nowrap;
      justify-content: space-between;
      width: 100%;
      a, button {
        background: none;
        border: 0;
        border-radius: 0;
        color: var(--linkcolor);
        font-family: inherit;
        font-size: inherit;
        font-weight: 400;
        letter-spacing: 1px;
        line-height: inherit;
        position: relative;
        text-decoration: none;
        text-transform: uppercase;
      }
      button { padding: 0; }
      a:hover, button:hover { color: var(--linkhover); }
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
      z-index: 10;
      .sitelinks {
        height: calc(100vh - 250px - 20px);
        margin-top: 250px;
        margin-left: 66px;
        flex-direction: column;
        justify-content: flex-start;
        width: 200px;
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
      width: 100%;
      z-index: 10;
      .sitelinks {
        width: calc(100% - 340px);
        margin-left: 320px;
        gap: clamp(16px, 3vw, 50px);
        justify-content: flex-start;
        & > div { flex-shrink: 0; }
        div.account {
          margin-left: auto;
          min-width: 0;
          flex-shrink: 1;
          button {
            display: block;
            max-width: 14rem;
            width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }
        a:before { display: none; }
      }
    }
    #content {
      padding-top: var(--navheight);
    }
  }

  /* Mobile Navigation */
  @media screen and (max-width: 900px) {
    body.leftnav, body.topnav {
      --navwidth: 0px;
      --navheight: 60px;
      #navigation {
        height: var(--navheight);
        width: 100%;
        line-height: normal;
        box-shadow: 0px 1px 2px #0003;
        z-index: 20;
        .menu-toggle {
          align-items: center;
          background: none;
          color: var(--linkcolor);
          display: flex;
          font-size: 28px;
          justify-content: center;
          position: absolute;
          top: 8px;
          right: 12px;
          width: 44px;
          height: 44px;
          padding: 0;
          border: 0;
          text-decoration: none;
          &:hover { color: var(--accent); }
        }
        .sitelinks {
          background: var(--bgcolor);
          box-shadow: 0px 4px 6px #0003;
          display: none;
          flex-direction: column;
          gap: 0;
          position: absolute;
          top: 100%;
          left: 0;
          width: 100%;
          height: auto;
          max-height: calc(100dvh - var(--navheight));
          overflow-y: auto;
          overscroll-behavior: contain;
          margin: 0;
          padding: 8px 16px 16px;
          & > div, div.account { margin: 0; padding: 0; flex-shrink: 0; }
          a, button, div.account button {
            display: block;
            width: 100%;
            max-width: none;
            min-height: 44px;
            padding: 12px 8px;
            line-height: 1.4;
            text-align: left;
            white-space: normal;
            overflow-wrap: anywhere;
            &:hover { background: var(--darkbg-bgs); }
          }
          a:before { display: none; }
        }
        &.menu-open .sitelinks { display: flex; }
      }
      #content { padding-left: 0; padding-top: var(--navheight); }
    }
  }

  /* Print */
  @media print {
    #navigation { display: none; }
    body.leftnav #content, body.topnav #content { padding: 0; }
  }

</style>
