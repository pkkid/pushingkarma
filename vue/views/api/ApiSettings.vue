<template>
  <div class='apioptions'>
    <Tooltip width='250px' text='An additonal Queries header is added to api requests
      detailing the count and duration of sql queries.'>
      <ToggleSwitch :value='countQueries' label='Count Queries' @update='setCountQueries'/>
    </Tooltip>
    <Tooltip width='250px' text='Enables server side logging of all sql queries and their duration.'>
      <ToggleSwitch :value='logQueries' label='Log Queries' @update='setLogQueries'/>
    </Tooltip>
  </div>
</template>

<script setup>
  import {inject} from 'vue'
  import {ToggleSwitch, Tooltip} from '@/components'
  import axios from 'axios'

  const {countQueries, setCountQueries} = inject('countQueries')  // Count queries on the server
  const {logQueries, setLogQueries} = inject('logQueries')        // Log queries on the server
</script>

<style>
  .apioptions {
    float: right;
    display: flex;
    flex-direction: column;
    font-size: 10px;
    gap: 3px;
  }
</style>
