<template>
  <div id='procswidget' class='widget' @click.stop='toggleSort'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>Processes</div>
      <div class='values'>{{glances.data.processcount?.total ?? '--'}} total</div>
    </div>
    <!-- Table -->
    <table v-if='procs.length' class='processlist'>
      <tr v-for='p in procs' :key='p.pid'>
        <td class='name'>{{p.name}}</td>
        <td class='mem'>{{utils.formatSize(p.mem)}}</td>
        <td class='cpu'>{{p.cpu.toPrecision(1)}}%</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
  import {computed, ref} from 'vue'
  import {useStorage} from '@/composables'
  import {utils} from '@/utils'
  import useGlances from '@/composables/useGlances'

  const glances = useGlances()  // Glances composable
  const shownum = 8  // Number of processes to show
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
      .mem {
        text-align: right;
        width: 150px;
      }
      .cpu {
        padding-right: 0px;
        text-align: right;
        width: 150px;
      }
    }
  }
</style>
