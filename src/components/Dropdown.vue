<template>
  <button class='dropdown' :style='{width}' v-on:click.prevent='showMenu=!showMenu' v-click-outside='clickOutside'>
    <slot name='text' v-on:click.prevent="showMenu=!showMenu">Default Text</slot>
    <transition name='custom-classes-transition'
        enter-active-class='animated fadeIn'
        leave-active-class='animated fadeOut'>
      <div v-if='showMenu' class='dropdown-menu' :style='{width:"calc("+width+" + 20px)"}'>
        <slot name='menu'>Default Menu</slot>
      </div>
    </transition>
  </button>
</template>

<script>
  export default {
    name: 'Dropdown',
    props: {
      width: {default: 'auto'},
    },
    data: () => ({
      showMenu: false,
    }),
    methods: {
      clickOutside: function() {
        this.showMenu = false;
      }
    },
  };
</script>

<style lang='scss'>
  .dropdown-menu {
    animation-duration: 0.2s;
  }
</style>
