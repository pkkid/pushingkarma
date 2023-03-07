<template>
  <div id='newtabwrap'>
    <div id='newtab'>
      <Photo ref='photo' v-if='width > 800'/>
      <Clock @click.native='$refs.photo.toggleDetails'/>
      <Events/>
      <IPAddr/>
      <News/>
      <Tasks/>
      <Weather/>
    </div>
  </div>
</template>

<script>
  import Clock from './NewTabClock';
  import Events from './NewTabEvents';
  import IPAddr from './NewTabIPAddr';
  import News from './NewTabNews';
  import Photo from './NewTabPhoto';
  import Tasks from './NewTabTasks';
  import Weather from './NewTabWeather';

  export default {
    name: 'NewTab',
    components: {Clock, Events, IPAddr, News, Photo, Tasks, Weather},
    data: () => ({
      width: window.innerWidth,
    }),
    mounted: function() {
      this.$store.set('global/layout', 'nonav');
    },
  };
</script>

<style lang='scss'>
  #newtabwrap {
    height: 100vh;
    width: 100%;
    background-color: #000;
    position: relative;
  }
  #newtab {
    background-color: #000;
    height: 100vh;
    font-size: 1rem;
    color: $newtab_color;
    font-family: 'Josefin Sans';
    position: relative;
    line-height: 1.5;
    text-shadow: 0px 1px 3px rgba(0,0,0,0.8);
    z-index: 10;
    a,a:hover,a:visited { color:$newtab_color; text-decoration:none; }
  }
  @media screen and (max-width: 970px) {
    $wiggle: 30px;
    #newtab {
      box-shadow: 0px 2px 10px rgba(0,0,0,0.5);
      color: $raspi_color;
      opacity: $raspi_opacity;
      cursor: none;
      text-shadow: none;
      height: calc(100vh - $wiggle);
      width: calc(100% - $wiggle);
      animation: square-move 3600s linear infinite;
      a,a:hover,a:visited { color:$raspi_color }
    }
    @keyframes square-move {
      0% { top:0; left:0; }
      25% { top:0; left:$wiggle; }
      50% { top:$wiggle; left:$wiggle; }
      75% { top:$wiggle; left:0; }
      100% { top:0; left:0; }
    }
  }
</style>
