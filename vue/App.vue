<template>
  <div id='layout' class='leftnav' @dblclick='toggleNav'>
    <div id='navigation'>
      <img class='logoimg' src='/static/img/pk.svg'/>
      <div class='logotxt'>PushingKarma</div>
      <!-- Primary Navigation Bar -->
      <div class='sitelinks'>
        <div><router-link to='/#splash'>Home</router-link></div>
        <div><router-link to='/#about'>About</router-link></div>
        <div><router-link to='/#projects'>Projects</router-link></div>
        <div><router-link to='/notes'>Notes</router-link></div>
        <div><router-link to='/budget'>Budget</router-link></div>  <!-- v-if='user.id' -->
      </div>
      <div id='socialicons'>
        <!-- <div><a class='iconwrap' href='https://github.com/pkkid'><b-icon icon='github-box'/></a></div> -->
        <!-- <div><a class='iconwrap' href='https://www.linkedin.com/in/shepanski'><b-icon icon='linkedin-box'/></a></div> -->
        <!-- <div><a class='iconwrap' href='https://www.facebook.com/mshepanski'><b-icon icon='facebook-box'/></a></div> -->
        <!-- <div @click='$refs.login.display=true'>
          <a v-if='user.id' class='iconwrap' href='javascript:void(0)'><i class='avatar' key='avatar' :style="{backgroundImage:avatar}"/></a>
          <a v-else class='iconwrap' href='javascript:void(0)'><b-icon icon='account-circle'/></a>
        </div> -->
      </div>
      <!-- <Login ref='login'/> -->
    </div>
    <div id='content' class='gridbg'><router-view></router-view></div>
  </div>
</template>

<script setup>
  import {onMounted} from 'vue'

  onMounted(() => checkDevFavicon()) 

  // Check Dev Favicon
  // Updates development favicon if domain is localhost
  const checkDevFavicon = function() {
    if (window.location.hostname == 'localhost') {
      let favicon = document.getElementById('favicon')
      favicon.href = '/static/img/devicon.ico'
    }
  }

  // Toggle Navigation
  // Toggle between topnav to leftnav
  const toggleNav = function() {
    let layout = document.getElementById('layout')
    layout.classList.toggle('topnav')
    layout.classList.toggle('leftnav')
  }
</script>

<style>
  #layout {
    min-height: 100vh;

    /* Base Navigation Styles */
    #navigation {
      color: #fbf1c7;
      background-color: #282828;
      position: fixed;
      font-family: 'Merriweather';
      .logoimg {
        position: absolute;
        z-index: 99;
      }
      .logotxt {
        color: #fbf1c7;
        font-family: 'Merriweather';
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 3px;
        line-height: 30px;
        position: absolute;
        text-align: center;
        text-transform: uppercase;
        z-index: 99;
      }
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
          &:hover { color:#fbf1c7; }
        }
      }
    }
    #content {
      min-height: 100vh;
      color: #111;
    }

    /* Left Navigation Menu */
    &.leftnav {
      --navwidth: 300px;
      #navigation {
        width: var(--navwidth);
        height: 100vh;
        .logoimg {
          left: calc((var(--navwidth) - 130px) / 2);
          top: 50px;
          width: 130px;
        }
        .logotxt {
          top: 150px;
          width: var(--navwidth);
        }
        .sitelinks {
          margin-top: 250px;
          margin-left: 66px;
          flex-direction: column;
          div { padding-bottom: 15px; }
        }
      }
      #content {
        margin-left: var(--navwidth);
      }
    }

    /* Top Navigation Menu */
    &.topnav {
      --navheight: 60px;
      line-height: var(--navheight);
      
      #navigation {
        width: 100vw;
        height: 60px;
        .logoimg {
          height: 40px;
          left: 20px;
          top: calc((var(--navheight) - 40px) / 2);
        }
        .logotxt {
          left: 100px;
          line-height: var(--navheight);
        }
        .sitelinks {
          width: 500px;
          margin-left: 320px;
        }
      }
      #content {
        padding-top: var(--navheight);
      }
    }
    
  }
</style>
