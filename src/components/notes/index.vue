<template>
  <div id='notes'>
    <Navigation :cls="'topnav'"/>
    <div class='sidebar'>
      <span id='search-icon' class='mdi mdi-magnify'></span>
      <input id='search' type='text' v-model='search' v-on:input='updateSearch'
        autofocus='true' spellcheck='false' autocomplete='off'>
    </div>
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
  import Navigation from '@/components/navigation'
  import Router from '@/router'

  export default {
    name: 'Notes',
    components: { Navigation },
    data() { return {
      search: '',
    }},
    beforeCreate: function() {
      this.$store.set('layout', 'topnav')
    },
    created: function() {
      this.search = this.$route.query.search
    },
    methods: {
      updateSearch: function() {
        Router.push({path:'/notes', query:{search:this.search}})
      },
    }
  }
</script>

<style lang='scss'>
  @import '@/assets/css/layout.scss';

  #notes .sidebar {
    position: fixed;
    top: 60px;
    left: 0;

    // Search Input
    #search {
      background-color: $dark-bgh;
      border-bottom: 1px solid rgba(0, 0, 0, 0.2);
      border-width: 0px;
      color: $light-yellow0;
      font-size: 20px;
      height: 40px;
      line-height: 40px;
      padding: 0px 10px 0px 40px;
      position: relative;
      width: 300px;
      &:focus {
        border-width: 0px;
        outline: none;
      }
    }
    #search-icon {
      font-size: 20px;
      left: 10px;
      line-height: 40px;
      position: absolute;
      top: 0px;
      z-index: 1;
    }
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
