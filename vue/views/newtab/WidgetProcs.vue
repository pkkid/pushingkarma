<template>
  <div id='procswidget' class='widget' @click.stop='toggleSort'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>Processes</div>
      <div class='values'>{{glances.data.processcount?.total ?? '--'}}</div>
    </div>
    <!-- Table -->
    <table v-if='procs.length' class='processlist'>
      <!-- <tr>
        <th class='name'>Name</th>
        <th class='cpu' :class='{selected: sortby == "cpu"}'>CPU</th>
        <th class='mem' :class='{selected: sortby == "mem"}'>Mem</th>
      </tr> -->
      <tr v-for='p in procs' :key='p.pid'>
        <td class='name'>{{p.name}}</td>
        <td class='cpu'>{{p.cpu.toFixed(2)}}%</td>
        <td class='mem'>{{utils.formatSize(p.mem)}}</td>
      </tr>
    </table>


    <!-- <div class='widget-title'>Processes <span class='sort-label'>sorted by {{sortBy === 'cpu' ? 'CPU' : 'Memory'}}</span></div>
    <table v-if='procs.length'>
      <thead>
        <tr>
          <th class='name-col'>Name</th>
          <th :class='{active: sortBy === "cpu"}'>CPU%</th>
          <th :class='{active: sortBy === "mem"}'>Mem</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for='p in procs' :key='p.pid'>
          <td class='name-col'>{{p.name}}</td>
          <td>{{p.cpu_percent.toFixed(1)}}%</td>
          <td>{{p.memory_mb}} MB</td>
        </tr>
      </tbody>
    </table>
    <div v-else class='no-data'>No data</div> -->
  </div>
</template>

<script setup>
  import {computed, ref} from 'vue'
  import {useStorage} from '@/composables'
  import {utils} from '@/utils'
  import useGlances from '@/composables/useGlances'

  const glances = useGlances()  // Glances composable
  const shownum = 6  // Number of processes to show
  const sortby = useStorage('newtab.procs.sortby', 'cpu')  // Sort by cpu or mem

  // List Processes
  // Compute a list of processes with name, pid, cpu%, mem, and user,
  const procs = computed(function() {
    const cores = glances.data?.cpu?.cpucore || 1
    return (glances.data?.processlist || []).map(p => ({
      name: p.name,
      pid: p.pid,
      cpu: p.cpu_percent / cores,
      mem: Math.round(p.memory_info?.rss),
      user: p.username,
    })).sort((a, b) => b[sortby.value] - a[sortby.value]).slice(0, shownum)
  })

  // Toggle Sort
  // Toggle sorting between CPU and Memory
  const toggleSort = function() {
    sortby.value = sortby.value === 'cpu' ? 'mem' : 'cpu'
  }
</script>

<style>
  #procswidget {
    .processlist {
      border-collapse: collapse;
      font-size: 0.9em;
      width: 100%;
      td {
        padding: 2px 10px;
        white-space: nowrap;
      }
      .name {
        overflow: hidden;
        padding-left: 0px;
        text-align: left;
        text-overflow: ellipsis;
      }
      .cpu {
        text-align: right;
        width: 170px;
      }
      .mem {
        padding-right: 0px;
        text-align: right;
        width: 170px;
      }
    }
  }
</style>
