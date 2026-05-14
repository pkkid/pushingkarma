<template>
  <div id='cpuwidget' class='widget'>
    <!-- Header -->
    <div class='header'>
      <div class='title'>
        {{glances.data.system?.hostname || 'CPU'}}
      </div>
      <div class='values'>
        {{glances.data.cpu?.total?.toPrecision(2) ?? '--'}}%
        <span class='delim'>|</span>
        {{utils.findItem(glances.data?.sensors, 'label', 'Package id 0', 'value') ?? 0}}°C
      </div>
    </div>
    <!-- Charts -->
    <div class='chartrow'>
      <div class='chartwrap cpu'>
        <span class='maxvalue'>100%</span>
        <Line v-if='cpudata' :data='cpudata' :options='cpuopts' :plugins='[cpuChartPlugin]'/>
      </div>
      <div class='chartwrap core1'>
        <Bar v-if='coredata1' :data='coredata1' :options='sutils.BAROPTS'/>
      </div>
      <div class='chartwrap core2'>
        <Bar v-if='coredata2' :data='coredata2' :options='sutils.BAROPTS'/>
      </div>
      <div class='chartwrap cputemp'>
        <span class='maxvalue'>{{glances.getMaxValue('cputemp')}}°C</span>
        <Line v-if='cputempdata' :data='cputempdata' :options='tempopts' :plugins='[tempChartPlugin]'/>
      </div>
    </div>
    <!-- Metrics -->
    <div class='metrics twocols'>
      <div><label>Freq:</label> {{((glances.data.quicklook?.cpu_hz_current ?? 0) / 1e9).toPrecision(3)}} GHz</div>
      <div><label>Coolant:</label> {{utils.findItem(glances.data?.sensors, 'label', 'Coolant temp', 'value') ?? '--'}}°C</div>
      <div><label>Uptime:</label> {{formatUptime(glances.data.uptime)}}</div>
      <div><label>Pump:</label> {{utils.findItem(glances.data?.sensors, 'label', 'Pump speed', 'value') ?? '--'}} rpm</div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line, Bar} from 'vue-chartjs'
  import {utils, sutils} from '@/utils'
  import useGlances from '@/composables/useGlances'
  Chart.register(...registerables)

  const glances = useGlances()    // Glances composable
  const OPTS = sutils.LINEOPTS    // Base line chart options

  // Setup CPU Usage Chart
  const cpuChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000})
  const cpuopts = {...OPTS, scales: {...OPTS.scales, y:{...OPTS.scales.y, max:100}}}
  glances.trackHistory('cpuusage', 60, (d) => d?.cpu?.total ?? 0)

  // Setup CPU Tempurature Chart
  const tempChartPlugin = sutils.scrollingChartPlugin({animateXDuration:2000, animateYDuration:300, maxy:100})
  const tempopts = {...OPTS, scales: {...OPTS.scales, y:{display:false, min:35}}}
  glances.trackHistory('cputemp', 30, (d) => utils.findItem(d?.sensors, 'label', 'Package id 0', 'value') ?? 0)

  // CPU Usage Data
  // Chart.js data object for CPU usage chart
  const cpudata = computed(function() {
    const h = glances.data?.history?.cpuusage
    if (!h?.length) { return null }
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: sutils.COLORS.BLUE,
        backgroundColor: `${sutils.COLORS.BLUE}33`,
        fill: true,
      }],
    }
  })

  // CPU Tempurature Data
  // Chart.js data object for CPU temperature chart
  const cputempdata = computed(function() {
    const h = glances.data?.history?.cputemp
    if (!h?.length) { return null }
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.value),
        borderColor: sutils.COLORS.ORANGE,
        backgroundColor: `${sutils.COLORS.ORANGE}33`,
        fill: true,
      }],
    }
  })

  // Get Core Data
  // Helper function to get Chart.js data object for even or odd indexed cores
  const getCoreData = function(evenodd='even') {
    const mod = evenodd === 'even' ? 0 : 1
    const cores = glances.data?.percpu?.filter((_, i) => i % 2 == mod)
    if (!cores?.length) { return null }
    return {
      labels: cores.map((_, i) => i),
      datasets: [{
        data: cores.map(c => c.total),
        backgroundColor: sutils.COLORS.BLUE,
        borderRadius: 2,
      }],
    }
  }

  // Core Data
  // Even-indexed cores in one chart
  const coredata1 = computed(function() { return getCoreData('even') })
  const coredata2 = computed(function() { return getCoreData('odd') })

  // Format Uptime
  // Parse Glances uptime string (e.g. '3 days, 12:14:05' or '6:01:36') and
  // return the two most significant non-zero components as '3d 12h', '12h 14m', etc.
  function formatUptime(str) {
    if (!str) { return '--' }
    const dayMatch = str.match(/(\d+)\s+day/)
    const timeMatch = str.match(/(\d+):(\d+):\d+/)
    if (!timeMatch) { return str }
    const days = dayMatch ? parseInt(dayMatch[1]) : 0
    const hours = parseInt(timeMatch[1])
    const mins = parseInt(timeMatch[2])
    const parts = [{v:days, s:'d'}, {v:hours, s:'h'}, {v:mins, s:'m'}]
    const start = parts.findIndex(p => p.v > 0)
    if (start === -1) { return '0m' }
    return parts.slice(start, start + 2).map(p => `${p.v}${p.s}`).join(' ')
  }
</script>

<style>
  #stats #cpuwidget {
    .chartrow {
      grid-template-columns: auto 150px;
      grid-template-rows: 50px 50px 70px;
      .cpu { grid-row:span 3; width:3fr; }
    }
  }
</style>
