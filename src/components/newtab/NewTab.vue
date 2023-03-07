<template>
  <div id='newtabwrap'>
    <div id='newtab' :class='daytime'>
      <Photo ref='photo' v-if='width > 800'/>
      <Clock @click.native='$refs.photo.toggleDetails'/>
      <Events/>
      <IPAddr/>
      <News/>
      <Tasks/>
      <Weather ref='weather'/>
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
  import * as dayjs from 'dayjs';

  export default {
    name: 'NewTab',
    components: {Clock, Events, IPAddr, News, Photo, Tasks, Weather},
    data: () => ({
      width: window.innerWidth,
      daytime: '',
    }),
    mounted: function() {
      this.$store.set('global/layout', 'nonav');
      setInterval(this.checkDaytime, 1000*60);
      this.checkDaytime();
    },
    methods: {
      checkDaytime: function() {
        if (!this.$refs.weather.weather) {
          this.daytime = 'day';
        } else {
          var now = dayjs().format('YYYY-MM-DDTHH:MM');
          var sunrise = this.$refs.weather.weather.daily[0].sunrise;
          var sunset = this.$refs.weather.weather.daily[0].sunset;
          console.log('---');
          console.log(`now: ${now}`);
          console.log(`sunrise: ${sunrise}`);
          console.log(`sunset: ${sunset}`);
          this.daytime = ((now < sunrise) || (now > sunset)) ? 'night' : 'day';
        }
      },
    }
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
      opacity: 1;
      cursor: none;
      text-shadow: none;
      height: calc(100vh - $wiggle);
      width: calc(100% - $wiggle);
      animation: square-move 1800s linear infinite;
      transition: opacity 5s;
      a,a:hover,a:visited { color:$raspi_color }
      &.day { opacity: 0.6; }
      &.night { opacity: 0.4; }
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
