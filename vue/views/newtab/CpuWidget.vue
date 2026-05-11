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
      <Line ref='lineRef' v-if='lineData' :data='lineData' :options='lineOptions'/>
    </div>
    <!-- Per-core Bar Chart -->
    <div class='chart-wrap cores-wrap'>
      <Bar v-if='coreData' :data='coreData' :options='barOptions'/>
    </div>
  </div>
</template>

<script setup>
  import {computed, ref, watch} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line, Bar} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  import chartScrollPlugin, {triggerChartScroll} from '@/utils/chartScrollPlugin'
  Chart.register(...registerables, chartScrollPlugin())

  const props = defineProps({animationDuration: {default: 300}, animationStyle: {default: 'ease'}})
  const {data, cpuHistory} = useGlances()
  const lineRef = ref(null)
  watch(cpuHistory, () => {
    const chart = lineRef.value?.chart
    if (chart?.$scroll) { chart.$scroll.duration = props.animationDuration; chart.$scroll.style = props.animationStyle }
    triggerChartScroll(chart)
  }, {flush: 'post'})

  const BLUE = 'rgba(69,133,136,0.9)'
  const BLUE_FILL = 'rgba(69,133,136,0.2)'

  const baseLineOpts = {
    animation: false,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
    scales: {
      x: {display: false},
      y: {display: false, min: 0, max: 100},
    },
    elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 2.5}},
  }

  const lineOptions = baseLineOpts
  const barOptions = {
    animation: false,
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
    const hz = data.value?.quicklook?.cpu_hz_current
    return hz ? (hz / 1e9).toFixed(2) : '--'
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
    .stat-big { font-size: 3em; font-weight: 600; line-height: 1; min-width: 4.5ch; text-align: right; flex-shrink: 0; }
    .stat-col { font-size: 0.95em; opacity: 0.75; line-height: 1.6; }
    .chart-wrap { height: 150px; width: 100%; }
    .cores-wrap { height: 50px; margin-top: 4px; }
  }
</style>
