<template>
  <button class='dropdown' :style='{width}' v-on:click.prevent="showMenu=!showMenu">
    <slot name='text' v-on:click.prevent="showMenu=!showMenu">Default Text</slot>
    <div v-if='showMenu' class='dropdown-menu' :style='{width:"calc("+width+" + 20px)"}'>
      <slot name='menu'>Default Menu</slot>
    </div>
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
  };
</script>


