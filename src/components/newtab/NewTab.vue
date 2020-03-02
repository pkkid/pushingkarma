<template>
  <div id='newtab' @dblclick='refreshPhoto'>
    <div id='photobg' :style='{backgroundImage:bgImage, opacity:photoOpacity}'/>
    <div id='photodetails' v-if='photo && showdetails'>
      <div class='title'><span v-if='photo.title'>{{photo.title}} |</span> {{photo.user}}</div>
      <div class='description'>{{photo.description}}</div>
    </div>
    <Clock @click.native='toggleDetails'/>
    <Events/>
    <IPAddr/>
    <News/>
    <Tasks/>
    <Weather/>
  </div>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
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
    },
    data: () => ({
      details: false,
      loaded: false,
      photo: null,
      photoOpacity: 0,
      showdetails: true,
    }),
    mounted: async function() {
      this.$store.set('global/layout', 'nonav');
      var {data} = await api.Tools.getPhoto();
      this.photo = data;
      await utils.preloadImage(this.photo.url);
      this.photoOpacity = 1;
    },
    methods: {
      refreshPhoto: async function() {
        this.photoOpacity = 0;
        await utils.sleep(500);
        var {data} = await api.Tools.refreshPhoto();
        this.photo = data;
        await utils.preloadImage(this.photo.url);
        this.photoOpacity = 1;
      },
      toggleDetails: function() {
        console.log('toggleDetails');
        this.showdetails = !this.showdetails;
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

    #photobg {
      width: 100%;
      height: 100vh;
      opacity: 0;
      background-position: center center;
      background-size: cover;
      transition: opacity 1s ease;
      z-index: 0;
    }

    #photodetails {
      background-color: $newtab_highlight;
      left: 50%;
      transform: translateX(-50%);
      position: absolute;
      top: 200px;
      max-width: 600px;
      color: $newtab_dim;
      display: table;
      margin: 0 auto;
      font-size: 12px;
      opacity: 1;
      top: 130px;
      transition: $newtab_transition_fast;
      background-color: rgba(0,0,0,0.6);
      border-radius: 4px;
      padding: 10px;
      .title { font-size:14px; float:left; padding-right:5px; }
      .description { clear:left; }
    }
  }
</style>
