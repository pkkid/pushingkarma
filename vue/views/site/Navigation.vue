<template>
  <div id='navigation' class='darkbg'>
    <!-- Animated Logo and Title -->
    <div id='logo'>
      <img src='/static/img/pk.svg'/>
      <div class='title'>PushingKarma</div>
    </div>
    <!-- Primary Navigation Bar -->
    <div id='leftnav'>
      <div class='pagelinks'>
        <div><router-link to='/#splash'>Home</router-link></div>
        <div><router-link to='/#about'>About</router-link></div>
        <div><router-link to='/#projects'>Projects</router-link></div>
        <div><router-link to='/notes'>Notes</router-link></div>
        <div><router-link to='/budget'>Budget</router-link></div>  <!-- v-if='user.id' -->
      </div>
      <div class='sociallinks'>
        <!-- <div><a class='iconwrap' href='https://github.com/pkkid'><b-icon icon='github-box'/></a></div> -->
        <!-- <div><a class='iconwrap' href='https://www.linkedin.com/in/shepanski'><b-icon icon='linkedin-box'/></a></div> -->
        <!-- <div><a class='iconwrap' href='https://www.facebook.com/mshepanski'><b-icon icon='facebook-box'/></a></div> -->
        <!-- <div @click='$refs.login.display=true'>
          <a v-if='user.id' class='iconwrap' href='javascript:void(0)'><i class='avatar' key='avatar' :style="{backgroundImage:avatar}"/></a>
          <a v-else class='iconwrap' href='javascript:void(0)'><b-icon icon='account-circle'/></a>
        </div> -->
      </div>
    </div>
    <!-- <Login ref='login'/> -->
  </div>
</template>

<script setup>
</script>

<style>
  #navigation {
    #logo {
      color: #fbf1c7;
      font-family: Merriweather;
      font-size: 15px;
      font-weight: bold;
      letter-spacing: 3px;
      position: relative;
      text-transform: uppercase;
      z-index: 99;
      img { width: 130px; }
    }
    #leftnav {
      /* font-family: $fontfamily-title; */
      background-color: #282828;
      font-size: 16px;
      font-weight: 400;
      height: 100vh;
      left: 0px;
      min-height: 600px;
      padding-top: 220px;
      position: fixed;
      top: 0px;
      width: 300px;
      z-index: 29;
    }
  }
</style>
