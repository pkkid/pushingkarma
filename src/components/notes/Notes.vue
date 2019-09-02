<template>
  <div id='notes'>
    <Navigation :cls="'topnav'"/>
    <div class='sidebar'><Search/></div>
    <div class='note'>
      Top Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
      Hello Notes<br/><br/><br/><br/><br/><br/><br/><br/>
    </div>
  </div>
</template>

<script>
  import Navigation from '../Navigation';
  import Search from './NotesSearch';

  export default {
    name: 'Notes',
    components: { Navigation, Search },
    beforeCreate: function() {
      this.$store.set('site/layout', 'topnav');
    },
  };
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #notes .sidebar {
    float: left;
    width: 300px;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

  // Note Layout
  #notes .note {
    background-color: #eee;
    box-sizing: border-box;
    color: $dark-bg0;
    margin-left: 300px;
    min-height: 100vh;
    margin-top: 60px;
  }
</style>
