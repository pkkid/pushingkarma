<template>
  <div id='notes'>
    <Navigation :cls="'topnav'"/>
    <div class='sidebar'>Sidebar</div>
    <div class='note'>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>
      Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>Hello Notes<br/>

    </div>
  </div>
</template>

<script>
  import Navigation from './Navigation.vue';

  export default {
    name: 'Notes',
    components: {Navigation},
    beforeCreate: function() {
      document.getElementById('logo').classList.add('topnav');
    }
  }
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #notes {
    background-color: #eee;
    border: 1px solid #444;
    box-sizing: border-box;
    color: $dark-bg0;
    margin-left: 300px;
    min-height: 100vh;
    margin-top: 60px;
    overflow-y: auto;
  }
</style>
