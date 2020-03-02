<template>
  <div id='newtab'>
    <Photo ref='photo'/>
    <Clock @click.native='$refs.photo.toggleDetails'/>
    <Events/>
    <IPAddr/>
    <News/>
    <Tasks/>
    <Weather/>
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
  };
</script>

<style lang='scss'>
  #newtab {
    background-color: #000;
    height: 100vh;
    font-size: 1.6rem;
    color: $newtab_color;
    font-family: 'Josefin Sans';
    position: relative;
    line-height: 1.5;
    text-shadow: 0px 1px 3px rgba(0,0,0,0.8);
    z-index: 10;
    a,a:hover,a:visited { color:$newtab_color; text-decoration:none; }
  }
</style>
