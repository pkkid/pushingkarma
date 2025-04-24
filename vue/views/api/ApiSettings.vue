<template>
  <div id='apisettings'>
    <Tooltip width='250px' text='Enabled axios history to be saved in the browser. Useful for debugging bad queries.'>
      <ToggleSwitch label='Save History' :value='axiosSettings.saveHistory.value' @update='axiosSettings.setSaveHistory'/>
    </Tooltip>
    <Tooltip width='250px' text='An additonal Queries header is added to api requests detailing the count and duration of sql queries.'>
      <ToggleSwitch label='Count Queries' :value='axiosSettings.countQueries.value' @update='axiosSettings.setCountQueries'/>
    </Tooltip>
    <Tooltip width='250px' text='Enables server side logging of all sql queries and their duration.'>
      <ToggleSwitch label='Log Queries' :value='axiosSettings.logQueries.value' @update='axiosSettings.setLogQueries'/>
    </Tooltip>
    <Tooltip width='250px' text='Artificially slows all api queries to 30s. Useful for testing loading states.'>
      <ToggleSwitch label='Slow Queries' :value='axiosSettings.slowQueries.value' @update='axiosSettings.setSlowQueries'/>
    </Tooltip>
  </div>
</template>

<script setup>
  import {inject, onMounted} from 'vue'
  import {ToggleSwitch, Tooltip} from '@/components'

  const axiosSettings = inject('axiosSettings')
</script>

<style>
  #apisettings {
    float: right;
    display: flex;
    flex-direction: column;
    gap: 1px;
    font-size: 13px;
    .toggle-switch, label { font-size: 10px; }
  }
</style>
