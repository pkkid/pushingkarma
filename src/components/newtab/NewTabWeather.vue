<template>
  <div id='weather'>
    <div class='weather-today'>
      <div class='weather-today-details'>
        <div class='weather-temp'>{toInt weather.currently.temperature}°F</div>
        <div class='weather-feelslike'>Feels: {toInt weather.currently.apparentTemperature}°</div>
      </div>
      <div class='weather-today-icon'>
        <i class='diw-{{ds2wuIcon weather.currently.icon}}'></i>
      </div>
      <div class='weather-today-summary'>
        <div class='weather-location'>Watertown</div>
        <div class='weather-description'>{weather.currently.summary}</div>
      </div>
    </div>
    <div class='forecast' style='clear:both'>
      {#withBefore weather.daily.data 5}
        <div class='forecast-day'>
          <div class='forecast-weekday'>{formatDate this.time '%a'}</div>
          <i class='diw-{ds2wuIcon this.icon}'></i>
          <div class='forecast-temp'>{toInt this.temperatureMax}°</div>
        </div>
      {/withBefore}
    </div>
  </div>
</template>

<script>
  export default {
    name: 'NewTabWeather',
  };
</script>

<style lang='scss'>
</style>
