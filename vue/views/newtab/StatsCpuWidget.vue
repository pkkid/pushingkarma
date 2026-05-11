<template>
  <div class='widget cpu-widget'>
    <div class='widget-title'>CPU: {{hostname}}</div>
    <div class='chart-row'>
      <!-- History Line Chart -->
      <div class='chart-wrap cpu-wrap'>
        <span class='current-value'>{{cpuTotal}}%</span>
        <Line ref='lineRef' v-if='lineData' :data='lineData' :options='lineOptions'/>
      </div>
      <!-- Per-core Bar Charts (two rows) -->
      <div class='cores-col'>
        <div class='chart-wrap cores-wrap'><Bar v-if='coreData1' :data='coreData1' :options='barOptions' :plugins='corePlugins'/></div>
        <div class='chart-wrap cores-wrap'><Bar v-if='coreData2' :data='coreData2' :options='barOptions' :plugins='corePlugins'/></div>
      </div>
    </div>
    <!-- Text rows -->
    <div class='stats-row' style='clear:left;'>
      <div class='stat-col'>
        <div>Temp: {{cpuTemp}}°C</div>
        <div>Freq: {{cpuFreq}} GHz</div>
        <div>Uptime: {{uptime}}</div>
      </div>
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
    animation: {duration: 300},
    responsive: true,
    maintainAspectRatio: false,
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
    scales: {
      x: {display: false},
      y: {display: false, min: 0, max: 100},
    },
  }

  const hostname = computed(() => data.value?.system?.hostname ?? 'CPU')
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

  const BLUE_TRACK = '#0000'

  const corePlugins = [{
    id: 'coreTrack',
    beforeDatasetsDraw(chart) {
      const {ctx, chartArea} = chart
      if (!chartArea) return
      const meta = chart.getDatasetMeta(0)
      ctx.save()
      ctx.fillStyle = BLUE_TRACK
      meta.data.forEach(bar => {
        ctx.beginPath()
        ctx.roundRect(bar.x - bar.width / 2, chartArea.top, bar.width, chartArea.height, 2)
        ctx.fill()
      })
      ctx.restore()
    },
  }]

  function makeCoreData(cores) {
    if (!cores?.length) return null
    return {
      labels: cores.map((_, i) => i),
      datasets: [{
        data: cores.map(c => c.total),
        backgroundColor: BLUE,
        borderRadius: 2,
      }],
    }
  }

  const coreData1 = computed(function() {
    const cores = data.value?.percpu
    if (!cores?.length) return null
    return makeCoreData(cores.filter((_, i) => i % 2 === 0))
  })

  const coreData2 = computed(function() {
    const cores = data.value?.percpu
    if (!cores?.length) return null
    return makeCoreData(cores.filter((_, i) => i % 2 === 1))
  })
</script>

<style>
  .cpu-widget {

    .chart-row {
      display: flex;
      gap: 5px;
      .cpu-chart { flex: 1; }
      .cores-col { display: flex; flex-direction: column; gap: 4px; width: 120px; flex-shrink: 0; }
      .cores-wrap { width: 120px; height:69px; flex-shrink: 0; margin-bottom:5px; }
    }

    .stats-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 6px;
    }
    .stat-big { font-size: 3em; font-weight: 600; line-height: 1; min-width: 4.5ch; text-align: right; flex-shrink: 0; }
    .stat-col { font-size: 0.95em; opacity: 0.75; line-height: 1.6; }
    .cores-wrap { height: 50px; }
  }
</style>
