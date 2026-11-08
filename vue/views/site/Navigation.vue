<template>
  <div id='navigation' class='darkbg'>
    <Logo @dblclick='showAccount=true'/>
    <Account :visible='showAccount' @close='showAccount=false'/>
    <div class='sitelinks'>
      <div class='home'><router-link to='/#splash'>Projects</router-link></div>
      <div class='notes'><router-link to='/notes'>Notes</router-link></div>
      <div class='budget' v-if='user?.id'><router-link to='/budget'>Budget</router-link></div>
      <div class='stocks' v-if='user?.id'><router-link to='/stocks'>Stocks</router-link></div>
      <div class='account' v-if='user?.id'><a href='#' @click.prevent @click='showAccount=true'>{{user.first_name}}</a></div>
      <div class='apidoc' v-if='user?.id'><a href='/apidoc'>API</a></div>
    </div>
    <ProjectList/>
  </div>
</template>

<script setup>
  import {inject, ref} from 'vue'
  import {ProjectList} from '@/views/projects'
  import {Account, Logo} from '@/views/site'

  const {user} = inject('user')
  const showAccount = ref(false)
</script>

<style>
  /* Base Navigation Styles */
  #navigation {
    .sitelinks {
      display: flex;
      flex-wrap: nowrap;
      justify-content: space-between;
      width: 100%;
      a {
        font-weight: 400;
        letter-spacing: 1px;
        position: relative;
        text-decoration: none;
        text-transform: uppercase;
      }
      /* Hover line grows under the link from left to right */
      a:before {
        background-color: var(--darkbg-bg0);
        bottom: -4px;
        content: "";
        height: 2px;
        left: 0px;
        position: absolute;
        transition: all .3s ease;
        width: 0px;
      }
      a:hover:before {
        background-color: var(--accent);
        width: 100%;
      }
    }
  }

  /* Left Navigation */
  body.leftnav {
    --navwidth: 300px;
    --navheight: 0px;
    #navigation {
      display: flex;
      flex-direction: column;
      height: 100vh;
      position: fixed;
      width: var(--navwidth);
      z-index: 10;
      /* Links sit side by side, wrapping when logged in adds more of them */
      .sitelinks {
        column-gap: 28px;
        flex-shrink: 0;
        flex-wrap: wrap;
        justify-content: center;
        margin: 212px 18px 34px 18px;
        row-gap: 12px;
        width: auto;
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
      z-index: 10;
      #projectlist { display: none; }
      .sitelinks {
        width: calc(100vw - 320px - 20px);
        margin-left: 320px;
        justify-content: flex-start;
        & > div { padding-right: 70px; }
        div.account { margin-left:auto; }
        div.account, div.api, div.apidoc {
          padding-right: 30px;
          a:hover:before { display: none; }
        }
      }
    }
    #content {
      padding-top: var(--navheight);
    }
  }

  /* Print */
  @media print {
    #navigation { display: none; }
    body.leftnav #content, body.topnav #content { padding: 0; }
  }

</style>
