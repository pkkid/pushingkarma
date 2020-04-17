<template>
  <transition name='custom-classes-transition' enter-active-class='animated fadeIn'>
    <div id='weather' :class='{showdetails}' v-if='weather'>
      <div class='weather-today'>
        <div class='weather-today-details' @click.prevent='toggleDetails'>
          <div class='weather-temp'>{{weather.currently.temperature | int}}°F</div>
          <div class='weather-feelslike'>Feels: {{weather.currently.apparentTemperature | int}}°</div>
        </div>
        <div class='weather-today-icon' @click.prevent='toggleDetails'>
          <i :class='[iconcls(weather.currently.icon)]'/>
        </div>
        <div class='weather-today-summary'>
          <div class='weather-location'>Watertown</div>
          <div class='weather-description'>{{weather.currently.summary}}</div>
        </div>
      </div>
      <div class='forecast' style='clear:both'>
        <div class='forecast-day' v-for='day in weather.daily.data.slice(0,5)' :key='day.time'>
          <div class='forecast-weekday'>{{day.time | formatDate('ddd')}}</div>
          <i :class='[iconcls(day.icon)]'/>
          <div class='forecast-temp'>{{day.temperatureMax| int }}°</div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
  import * as api from '@/api';
  import * as utils from '@/utils/utils';
  require('@/assets/font/dripicons/dripicons-weather.css');

  export default {
    name: 'NewTabWeather',
    data: () => ({
      weather: null,
      showdetails: false,
    }),
    mounted: async function() {
      this.update();
      setInterval(this.update, 1000*60*5);
    },
    methods: {
      iconcls: function(icon) {
        return `diw-${utils.ds2wuIcon(icon)}`;
      },
      toggleDetails: function() {
        this.showdetails = !this.showdetails;
      },
      update: async function() {
        var {data} = await api.Tools.getWeather();
        this.weather = data;
      }
    },
  };
</script>

<style lang='scss'>
  #weather {
    position: absolute;
    right: 20px;
    top: 20px;
    transition: $newtab_transition;
    width: 350px;
    .weather-today {
      font-size: 16px;
      line-height: 14px;
      text-align: right;
      & > div { float:right; padding-left:20px; }
      .weather-location { font-size:25px; line-height:27px; padding:4px 0px 4px 0px;}
      .weather-today-icon { font-size:50px; cursor:pointer; }
      .weather-temp { font-size:35px; line-height:36px; }
      .weather-today-details { cursor:pointer; }
    }
    .weather-today-summary {
      opacity: 0;
      transition: $newtab_transition;
    }
    .forecast {
      color: $newtab_dim;
      float: right;
      font-size: 14px;
      line-height: 16px;
      padding-top: 20px;
      width: 275px;
      opacity: 0;
      transition: $newtab_transition;
      .forecast-day { width:30px; margin-left:25px; text-align:center; float:left; }
      .forecast-weekday { padding-bottom:2px; }
      [class^='diw-']:before { font-size:20px; }
      .forecast-temp { padding-top:6px; }
    }
    &.showdetails {
      .weather-today-summary { opacity: 1; }
      .forecast { opacity: 1; }
    }
  }
  @media screen and (max-width: 1100px) {
    #weather { right:20px; top:20px; width:350px;
      .weather-today-summary { opacity:1; }
      .forecast { opacity:1; }
    }
  }
  @media screen and (max-width: 800px) {
    #weather .forecast { color: $raspi_dim; }
  }
</style>
