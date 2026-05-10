<template>
  <div class='glances-widget processes-widget'>
    <div class='widget-title'>Processes</div>
    <table v-if='procs.length'>
      <thead>
        <tr>
          <th class='name-col'>Name</th>
          <th>CPU%</th>
          <th>Mem%</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for='p in procs' :key='p.pid'>
          <td class='name-col'>{{p.name}}</td>
          <td>{{p.cpu_percent.toFixed(1)}}%</td>
          <td>{{p.memory_percent.toFixed(1)}}%</td>
        </tr>
      </tbody>
    </table>
    <div v-else class='no-data'>No data</div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import useGlances from '@/composables/useGlances'

  const {data} = useGlances()

  const procs = computed(function() {
    const list = data.value?.processlist
    if (!list?.length) return []
    return [...list]
      .sort((a, b) => b.cpu_percent - a.cpu_percent)
      .slice(0, 6)
  })
</script>

<style>
  .processes-widget {
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 1em;
    }
    th, td {
      padding: 5px 8px;
      text-align: right;
      white-space: nowrap;
    }
    th { opacity: 0.5; font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.1); }
    td { opacity: 0.85; }
    .name-col { text-align: left; max-width: 140px; overflow: hidden; text-overflow: ellipsis; }
    tr:nth-child(even) td { background: rgba(255,255,255,0.04); }
    .no-data { opacity: 0.4; font-size: 1em; }
  }
</style>
