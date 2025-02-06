<template>
  <div id='navigation'>
    <Logo/>
    <div class='sitelinks'>
      <div><router-link to='/#splash'>Home</router-link></div>
      <div><router-link to='/#projects'>Projects</router-link></div>
      <div><router-link to='/notes'>Notes</router-link></div>
      <div><router-link to='/budget'>Budget</router-link></div>
    </div>
  </div>
</template>

<script setup>
  import Logo from '@/views/site/Logo.vue'
</script>

<style>
  /* Base Navigation Styles */
  #navigation {
    color: #fbf1c7;
    background-color: #282828;
    position: fixed;
    font-family: 'Merriweather';
    .sitelinks {
      color: #fbf1c7;
      display: flex;
      flex-wrap: nowrap;
      justify-content: space-between;
      a {
        color: #fbf1c7;
        text-decoration: none;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 400;
        position: relative;
        transition: color .1s ease;
        &:hover { color:#fbf1c7; }
      }
      a:hover {
        color: #fe8019;
      }
      a:before {
        background-color: #fe8019;
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
        background-color: #fe8019;
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
