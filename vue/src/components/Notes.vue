<template>
  <div id='notes'>
    <div class='sidebar'>Sidebar</div>
    <div class='note'>Hello Notes</div>
  </div>
</template>

<script>
  export default {
    name: 'Notes',
    beforeCreate: function() {
      document.getElementById('navigation').classList.add('topnav');
    }
  }
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #notes {
    padding-top: 60px;
    box-sizing: border-box;
    border: 1px solid #444;
    min-height: 100vh;
    background-color: #eee;
    color: $dark-bg0;
  }
</style>
