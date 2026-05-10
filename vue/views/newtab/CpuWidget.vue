<template>
  <div class='glances-widget cpu-widget'>
    <div class='widget-title'>CPU</div>
    <div class='stats-row'>
      <span class='stat-big'>{{cpuTotal}}%</span>
      <div class='stat-col'>
        <div>Temp: {{cpuTemp}}°C</div>
        <div>Freq: {{cpuFreq}} GHz</div>
        <div>Uptime: {{uptime}}</div>
      </div>
    </div>
    <!-- History Line Chart -->
    <div class='chart-wrap'>
      <Line v-if='lineData' :data='lineData' :options='lineOptions'/>
    </div>
    <!-- Per-core Bar Chart -->
    <div class='chart-wrap cores-wrap'>
      <Bar v-if='coreData' :data='coreData' :options='barOptions'/>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line, Bar} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const {data, cpuHistory} = useGlances()

  const BLUE = 'rgba(69,133,136,0.9)'
  const BLUE_FILL = 'rgba(69,133,136,0.2)'

  const baseLineOpts = {
    animation: {duration: 300},
    responsive: true,
    maintainAspectRatio: false,
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
    scales: {
      x: {display: false},
      y: {display: false, min: 0, max: 100},
    },
    elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 1.5}},
  }

  const lineOptions = baseLineOpts
  const barOptions = {
    animation: {duration: 300},
    responsive: true,
    maintainAspectRatio: false,
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
    scales: {
      x: {display: false},
      y: {display: false, min: 0, max: 100},
    },
  }

  const cpuTotal = computed(() => data.value?.cpu?.total?.toFixed(1) ?? '--')

  const cpuTemp = computed(function() {
    const sensors = data.value?.sensors || []
    const pkg = sensors.find(s => s.label === 'Package id 0')
    return pkg ? pkg.value : '--'
  })

  const cpuFreq = computed(function() {
    const freq = data.value?.percpu?.[0]
    if (!freq) return '--'
    // glances exposes cpu_freq via the quicklook plugin; fall back to showing core count
    const cpufreq = data.value?.quicklook?.cpu_freq
    if (cpufreq) return (cpufreq / 1000).toFixed(2)
    return '--'
  })

  const uptime = computed(() => data.value?.uptime ?? '--')

  const lineData = computed(function() {
    const h = cpuHistory.value
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: BLUE,
        backgroundColor: BLUE_FILL,
        fill: true,
      }],
    }
  })

  const coreData = computed(function() {
    const cores = data.value?.percpu
    if (!cores?.length) return null
    return {
      labels: cores.map((_, i) => i),
      datasets: [{
        data: cores.map(c => c.total),
        backgroundColor: BLUE,
        borderRadius: 2,
      }],
    }
  })
</script>

<style>
  .cpu-widget {
    .stats-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 6px;
    }
    .stat-big { font-size: 3em; font-weight: 600; line-height: 1; }
    .stat-col { font-size: 0.95em; opacity: 0.75; line-height: 1.6; }
    .chart-wrap { height: 80px; width: 100%; }
    .cores-wrap { height: 50px; margin-top: 4px; }
  }
</style>
