<template>
  <div id='photo'>
    <div class='title'>{this.photo.title} {#if this.photo.title}|{/if} {this.photo.user}</div>
    <span class='mdi mdi-autorenew'></span>
    <div class='description'>{this.photo.description}</div>
  </div>
</template>

<script>
  export default {
    name: 'NewTabPhoto',
  };
</script>

<style lang='scss'>
</style>
