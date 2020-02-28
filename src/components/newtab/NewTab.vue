<template>
  <div id='newtab'>
    <Clock/>
    <Tasks/>
    <IPAddr/>
    <div id='photo' class='hidedetails'></div>
    <div id='calendar'></div>
    <div id='weather' class='hidedetails'></div>
    <div id='news'></div>
  </div>
</template>

<script>
  import Clock from './NewTabClock';
  import Tasks from './NewTabTasks';
  import IPAddr from './NewTabIPAddr';

  export default {
    name: 'NewTab',
    components: {Clock, Tasks, IPAddr},
    mounted: function() {
      this.$store.set('global/layout', 'nonav');
    },
  };
</script>

<style lang='scss'>
  
  #newtab {
    background-color: black;
    height: 100vh;
    font-size: 1.6rem;
    color: $newtab_color;
    font-family: 'Josefin Sans';
    position: relative;
    line-height: 1.5;
    text-shadow: 0px 1px 3px rgba(0,0,0,0.8);
    a,a:hover,a:visited { color:$newtab_color; text-decoration:none; }
  }
</style>
