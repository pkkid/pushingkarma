<template>
  <div class='widget network-widget'>
    <div class='widget-title'>Network</div>
    <div class='chart-wrap'>
      <Line ref='lineRef' v-if='lineData' :data='lineData' :options='lineOptions'/>
    </div>
    <table v-if='ifaces.length'>
      <tbody>
        <tr v-for='iface in ifaces' :key='iface.name'>
          <td class='iface-ip'>{{iface.ip}}</td>
          <td class='speed'><span class='up'>↑</span> {{iface.sent}}</td>
          <td class='speed'><span class='dn'>↓</span> {{iface.recv}}</td>
        </tr>
      </tbody>
    </table>
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
  const lineRef = ref(null)
  watch(netHistory, () => {
    const chart = lineRef.value?.chart
    if (chart?.$scroll) { chart.$scroll.duration = props.animationDuration; chart.$scroll.style = props.animationStyle }
    const h = netHistory.value
    const peak = Math.max(...h.map(p => Math.max(p.sent, p.recv)), 1)
    animateYMax(chart, peak)
    triggerChartScroll(chart)
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

  const lineOptions = {
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

  const lineData = computed(function() {
    const h = netHistory.value
    if (!h.length) return null
    return {
      labels: h.map(() => ''),
      datasets: [
        {
          label: 'Upload',
          data: h.map(p => p.sent),
          borderColor: UP_COLOR,
          backgroundColor: UP_FILL,
          fill: true,
        },
        {
          label: 'Download',
          data: h.map(p => p.recv),
          borderColor: DN_COLOR,
          backgroundColor: DN_FILL,
          fill: true,
        },
      ],
    }
  })
</script>

<style>
  .network-widget {
    .chart-wrap { height: 150px; width: 100%; margin-bottom: 8px; }
    table { width: 100%; border-collapse: collapse; font-size: 1em; table-layout: fixed; }
    td { padding: 4px 8px; opacity: 0.85; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .iface-name { opacity: 0.55; }
    .iface-ip { opacity: 0.55; font-size: 0.85em; width: 40%; }
    .speed { text-align: right; width: 45%; }
    .up { color: rgba(214,93,14,0.9); }
    .dn { color: rgba(69,133,136,0.9); }
  }
</style>
