<template>
  <div id='weather' v-if='loaded'>
    <div class='weather-today'>
      <div class='weather-today-details'>
        <div class='weather-temp'>{{weather.currently.temperature | int}}°F</div>
        <div class='weather-feelslike'>Feels: {{weather.currently.apparentTemperature | int}}°</div>
      </div>
      <div class='weather-today-icon'>
        <!-- <i class='diw-{{weather.currently.icon | ds2wuIcon}}'></i> -->
      </div>
      <div class='weather-today-summary'>
        <div class='weather-location'>Watertown</div>
        <div class='weather-description'>{{weather.currently.summary}}</div>
      </div>
    </div>
    <div class='forecast' style='clear:both'>
      <div class='forecast-day' v-for='day in weather.daily.data.slice(0,5)' :key='day.time'>
        <div class='forecast-weekday'>{{day.time | formatDate('ddd')}}</div>
        <!-- <i class='diw-{{day.icon | ds2wuIcon}}'></i> -->
        <div class='forecast-temp'>{{day.temperatureMax| int }}°</div>
      </div>
    </div>
  </div>
</template>

<script>
  import * as api from '@/api';

  export default {
    name: 'NewTabWeather',
    data: () => ({
      loaded: false,
      weather: null,
    }),
    mounted: async function() {
      var {data} = await api.Tools.getWeather();
      this.weather = data;
      this.loaded = true;
    },
  };
</script>

<style lang='scss'>
  #weather {
    background-color: $newtab_highlight;
    position: absolute;
    right: 20px;
    top: 20px;
    transition: $newtab_transition_slow;
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
    .forecast {
      color: $newtab_dim;
      float: right;
      font-size: 14px;
      line-height: 16px;
      padding-top: 20px;
      width: 275px;
      transition: $newtab_transition_fast;
      .forecast-day { width:30px; margin-left:25px; text-align:center; float:left; }
      .forecast-weekday { padding-bottom:2px; }
      [class^='diw-']:before { font-size:20px; }
      .forecast-temp { padding-top:6px; }
    }
    .weather-today-summary { transition: $newtab_transition_fast; }
    &.hidedetails { .weather-today-summary,.forecast { opacity:0; }}
  }
</style>
