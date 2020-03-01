<template>
  <div id='newtab' @dblclick='refreshPhoto'>
    <div id='bg' :style='{backgroundImage:bgImage, opacity:bgOpacity}'/>
    <Clock/>
    <Events/>
    <IPAddr/>
    <News/>
    <Tasks/>
    <Weather/>
  </div>
</template>

<script>
  import * as api from '@/api';
  import Clock from './NewTabClock';
  import Events from './NewTabEvents';
  import IPAddr from './NewTabIPAddr';
  import News from './NewTabNews';
  import Tasks from './NewTabTasks';
  import Weather from './NewTabWeather';

  export default {
    name: 'NewTab',
    components: {Clock, Events, IPAddr, News, Tasks, Weather},
    computed: {
      bgImage: function() { return this.photo ? 'url("'+ this.photo.url +'")' : ''; },
      bgOpacity: function() { return this.photo ? 1 : 0; },
    },
    data: () => ({
      loaded: false,
      photo: null,
      details: false,
    }),
    mounted: async function() {
      this.$store.set('global/layout', 'nonav');
      this.refreshPhoto();      
    },
    methods: {
      refreshPhoto: async function() {
        console.log('getPhoto');
        var {data} = await api.Tools.getPhoto();
        this.photo = data;
      },
    },
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

    #bg {
      width: 100%;
      height: 100vh;
      opacity: 0;
      background-position: center center;
      background-size: cover;
      transition: opacity 1s ease;
      z-index: 0;
    }
  }
</style>
