<template>
  <div id='notes'>
    <Navigation :cls="'topnav'"/>
    <div class='sidebar'>
      <Search/>
    </div>
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
  import Navigation from '@/components/navigation'
  import Search from '@/components/notes/search'

  export default {
    name: 'Notes',
    components: { Navigation, Search },
    beforeCreate: function() {
      this.$store.set('site/layout', 'topnav')
    },
  }
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #notes .sidebar {
    position: fixed;
    top: 60px;
    left: 0;
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
