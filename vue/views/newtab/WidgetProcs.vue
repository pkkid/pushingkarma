<template>
  <div class='widget processes-widget' @click.stop='toggleSort'>
    <div class='widget-title'>Processes <span class='sort-label'>sorted by {{sortBy === 'cpu' ? 'CPU' : 'Memory'}}</span></div>
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
    <div v-else class='no-data'>No data</div>
  </div>
</template>

<script setup>
  import {computed, ref, watch} from 'vue'
  import useGlances from '@/composables/useGlances'

  const {data, host} = useGlances()
  const sortBy = ref('cpu')       // 'cpu' or 'mem'
  const memList = ref([])         // processlist fetched sorted by memory

  const toggleSort = function() {
    sortBy.value = sortBy.value === 'cpu' ? 'mem' : 'cpu'
  }

  // Fetch memory-sorted processlist from Glances directly
  const fetchMemList = async function() {
    try {
      const res = await fetch(`${host.value}/api/4/processlist`)
      if (!res.ok) return
      const list = await res.json()
      memList.value = list
    } catch (e) { /* ignore */ }
  }

  // Re-fetch memory list whenever main data updates (same cadence as poll)
  watch(data, function() {
    if (sortBy.value === 'mem') fetchMemList()
  })

  // Fetch immediately when switching to mem sort
  watch(sortBy, function(val) {
    if (val === 'mem') fetchMemList()
  })

  const procs = computed(function() {
    const cores = data.value?.cpu?.cpucore || 1
    const totalMem = data.value?.mem?.total || 0
    const toRow = p => ({
      ...p,
      cpu_percent: p.cpu_percent / cores,
      memory_mb: Math.round(p.memory_percent / 100 * totalMem / 1024 / 1024),
    })
    if (sortBy.value === 'mem') {
      if (!memList.value?.length) return []
      return [...memList.value]
        .sort((a, b) => b.memory_percent - a.memory_percent)
        .slice(0, 6)
        .map(toRow)
    }
    const list = data.value?.processlist
    if (!list?.length) return []
    return [...list]
      .sort((a, b) => b.cpu_percent - a.cpu_percent)
      .slice(0, 6)
      .map(toRow)
  })
</script>

<style>
  .processes-widget {
    .sort-label { opacity: 0.5; font-size: 0.85em; margin-left: 6px; }
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
    th.active { opacity: 0.9; }
    td { opacity: 0.85; }
    .name-col { text-align: left; max-width: 140px; overflow: hidden; text-overflow: ellipsis; }

    .no-data { opacity: 0.4; font-size: 1em; }
  }
</style>
