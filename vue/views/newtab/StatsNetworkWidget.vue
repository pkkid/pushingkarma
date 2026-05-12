<template>
  <div class='widget network-widget'>
    <div class='widget-title'>
      Network

    </div>
    <div class='chart-wrap' style='height:100px; margin-bottom:0px;'>
      <div class='current-value'><span class='up'>↑</span> {{currentSent}}</div>
      <Line ref='upRef' v-if='upData' :data='upData' :options='upOptions'/>
    </div>
    <div class='chart-wrap' style='height:100px;'>
      <div class='current-value'><span class='dn'>↓</span> {{currentRecv}}</div>
      <Line ref='dnRef' v-if='dnData' :data='dnData' :options='dnOptions'/>
    </div>
    <!-- Text rows -->
    <div class='stats-row' style='clear:left;'>
      <div class='stat-col'>
        <div>Intenral IP: {{data?.ip?.address}}</div>
        <div>External IP: {{data?.ip?.public_address}}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed, ref, watch} from 'vue'
  import {Chart, registerables} from 'chart.js'
  import {Line} from 'vue-chartjs'
  import useGlances from '@/composables/useGlances'
  import chartScrollPlugin, {triggerChartScroll, animateYMax} from '@/utils/chartScrollPlugin'
  Chart.register(...registerables, chartScrollPlugin())

  const props = defineProps({animationDuration: {default: 300}, animationStyle: {default: 'ease'}})
  const {data, netHistory} = useGlances()
  const upRef = ref(null)
  const dnRef = ref(null)
  watch(netHistory, () => {
    const upChart = upRef.value?.chart
    const dnChart = dnRef.value?.chart
    const h = netHistory.value
    const peakUp = Math.max(...h.map(p => p.sent), 1)
    const peakDn = Math.max(...h.map(p => p.recv), 1)
    for (const [chart, peak] of [[upChart, peakUp], [dnChart, peakDn]]) {
      if (chart?.$scroll) { chart.$scroll.duration = props.animationDuration; chart.$scroll.style = props.animationStyle }
      animateYMax(chart, peak)
      triggerChartScroll(chart)
    }
  }, {flush: 'post'})

  const UP_COLOR = 'rgba(214,93,14,0.9)'
  const DN_COLOR = 'rgba(69,133,136,0.9)'
  const UP_FILL = 'rgba(214,93,14,0.15)'
  const DN_FILL = 'rgba(69,133,136,0.15)'

  function fmtSpeed(bytesPerSec) {
    if (bytesPerSec >= 1024 * 1024) return (bytesPerSec / (1024 * 1024)).toFixed(1) + ' MB/s'
    if (bytesPerSec >= 1024) return (bytesPerSec / 1024).toFixed(1) + ' KB/s'
    return bytesPerSec.toFixed(0) + ' B/s'
  }

  const currentSent = computed(() => { const h = netHistory.value; return h.length ? fmtSpeed(h[h.length-1].sent) : '0 B/s' })
  const currentRecv = computed(() => { const h = netHistory.value; return h.length ? fmtSpeed(h[h.length-1].recv) : '0 B/s' })

  const ifaces = computed(function() {
    const list = data.value?.network || []
    const primaryIp = data.value?.ip?.address || ''
    const filtered = list.filter(i => i.interface_name !== 'lo' && i.speed > 0)
    return filtered.map((i, idx) => ({
      name: i.interface_name,
      ip: idx === 0 ? primaryIp : '',
      sent: fmtSpeed(i.bytes_sent_rate_per_sec || 0),
      recv: fmtSpeed(i.bytes_recv_rate_per_sec || 0),
    }))
  })

  const baseOptions = {
    animation: false,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {legend: {display: false}, tooltip: {enabled: false}},
    scales: {
      x: {display: false},
      y: {display: false, min: 0},
    },
    elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 2.5}},
  }
  const upOptions = baseOptions
  const dnOptions = {...baseOptions, scales: {...baseOptions.scales, y: {...baseOptions.scales.y, reverse: true}}}

  const upData = computed(function() {
    const h = netHistory.value
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.sent),
        borderColor: UP_COLOR,
        backgroundColor: UP_FILL,
        fill: true,
      }],
    }
  })

  const dnData = computed(function() {
    const h = netHistory.value
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [{
        data: h.map(p => p.recv),
        borderColor: DN_COLOR,
        backgroundColor: DN_FILL,
        fill: true,
      }],
    }
  })
</script>

<style>
  .network-widget {
    .chart-wrap { flex: 1; min-width: 0; position: relative; height: 80px; }
    .chart-label { font-size: 0.75em; opacity: 0.6; margin-bottom: 2px; }
    .chart-label.up { color: rgba(214,93,14,0.9); }
    .chart-label.dn { color: rgba(69,133,136,0.9); }
    table { width: 100%; border-collapse: collapse; font-size: 1em; table-layout: fixed; }
    td { padding: 4px 8px; opacity: 0.85; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .iface-name { opacity: 0.55; }
    .iface-label { opacity: 0.55; font-size: 0.85em; width: 15%; }
    .iface-ip { opacity: 0.55; font-size: 0.85em; width: 40%; }
    .ext-ip { width: auto; }
    .speed { text-align: right; width: 45%; }
    .up { color: rgba(214,93,14,0.9); }
    .dn { color: rgba(69,133,136,0.9); }
  }
</style>
