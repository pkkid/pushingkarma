<template>
  <div id='navigation' class='darkbg'>
    <div class='menu'>
      Navigation Component
      <div><router-link to='/#splash'>Home</router-link></div>
      <div><router-link to='/#about'>About</router-link></div>
      <div><router-link to='/#projects'>Projects</router-link></div>
      <div><router-link to='/notes'>Notes</router-link></div>
      <!-- <div v-if='user.id'><router-link to='/budget'>Budget</router-link></div> -->
    </div>
    <div class='links'>
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
</template>

<script setup>
</script>

<style>
  #navigation {
    /* font-family: $fontfamily-title; */
    font-weight: 400;
    font-size: 16px;
    position: fixed;
    width: 300px;
    height: 100vh;
    top: 0px;
    left: 0px;
    min-height: 600px;
    padding-top: 220px;
    z-index: 29;
  }
</style>
