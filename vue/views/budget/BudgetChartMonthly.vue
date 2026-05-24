<template>
  <BudgetChart v-if='chartDatasets' v-slot='{isExpanded, isReady}'>
    <Bar v-if='isReady' :options='chartOptions(isExpanded)' :data='chartDatasets'/>
  </BudgetChart>
</template>

<script setup>
  import {computed, onMounted, ref, watch} from 'vue'
  import {Bar} from 'vue-chartjs'
  import {Chart, registerables} from 'chart.js'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'
  import BudgetChart from './BudgetChart.vue'
  Chart.register(...registerables)

  const props = defineProps({
    months: {type:Number, default:24},
  })
  var cancelctrl = null                         // Cancel controller for monthly spending
  const monthlyData = ref(null)                 // Monthly spending data
  const {search} = useUrlParams({search:{}})    // Search string from URL

  // Apply date filter from chart click
  // Replaces existing date="..." token, then appends the clicked month-year
  const applyChartDateFilter = function(label) {
    if (!label) { return }
    var token = `date="${label}"`
    var cleaned = (search.value || '').replace(/\bdate="[^"]+"/g, '').replace(/\s+/g, ' ').trim()
    search.value = cleaned ? `${cleaned} ${token}` : token
  }

  // Handle chart clicks using tooltip-like index mode (intersect:false)
  const onChartClick = function(evt, activeEls, chart) {
    var els = chart.getElementsAtEventForMode(evt, 'index', {intersect: false}, false)
    if (!els || !els.length) { return }
    var idx = els[0].index
    if (idx == null) { return }
    var label = chart?.data?.labels?.[idx]
    applyChartDateFilter(label)
  }

  // Chart Datasets
  // Build chart.js dataset from monthly spending data
  const chartDatasets = computed(function() {
    if (!monthlyData.value) { return null }
    return {
      labels: monthlyData.value.labels.map(function(d) {
        return utils.formatDate(d, 'MMM YYYY')
      }),
      datasets: [{
        label: 'Spending',
        data: monthlyData.value.spending,
        backgroundColor: '#cc241d',
        borderColor: '#cc241d',
        borderWidth: 1,
        borderRadius: 2,
      }, {
        label: 'Income',
        data: monthlyData.value.income,
        backgroundColor: '#98971a',
        borderColor: '#98971a',
        borderWidth: 1,
        borderRadius: 2,
      }]
    }
  })

  // Chart Options
  // Build chart.js options, switching between mini and expanded modes
  const chartOptions = function(isExpanded) {
    var opts = {}
    utils.rset(opts, 'animation.duration', 0)
    utils.rset(opts, 'events', ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'])
    utils.rset(opts, 'onClick', onChartClick)
    utils.rset(opts, 'plugins.legend.align', 'end')
    utils.rset(opts, 'plugins.legend.display', true)
    utils.rset(opts, 'plugins.legend.labels.boxHeight', 7)
    utils.rset(opts, 'plugins.legend.labels.boxWidth', 7)
    utils.rset(opts, 'plugins.legend.position', 'top')
    utils.rset(opts, 'plugins.title.align', 'start')
    utils.rset(opts, 'plugins.title.color', 'var(--lightbg-fg1)')
    utils.rset(opts, 'plugins.title.display', true)
    utils.rset(opts, 'plugins.title.font.size', 15)
    utils.rset(opts, 'plugins.title.padding.bottom', -23)
    utils.rset(opts, 'plugins.title.text', 'Monthly Spend')
    utils.rset(opts, 'plugins.tooltip.callbacks.label', (ctx) => ` ${ctx.dataset.label}: ${utils.usd(ctx.parsed.y, 0)}`)
    utils.rset(opts, 'plugins.tooltip.enabled', true)
    utils.rset(opts, 'plugins.tooltip.intersect', false)
    utils.rset(opts, 'plugins.tooltip.mode', 'index')
    utils.rset(opts, 'scales.x.display', true)
    utils.rset(opts, 'scales.x.ticks.font.size', 9)
    utils.rset(opts, 'scales.x.ticks.maxTicksLimit', 12)
    utils.rset(opts, 'scales.y.display', true)
    utils.rset(opts, 'scales.y.ticks.callback', (value) => utils.usd(value, 0, '$', 3))
    utils.rset(opts, 'scales.y.ticks.font.size', 9)
    if (!isExpanded) {
      utils.rset(opts, 'animation.duration', 0)
      utils.rset(opts, 'events', [])
      utils.rset(opts, 'layout.padding.bottom', 0)
      utils.rset(opts, 'layout.padding.left', 0)
      utils.rset(opts, 'layout.padding.right', 0)
      utils.rset(opts, 'layout.padding.top', 0)
      utils.rset(opts, 'maintainAspectRatio', false)
      utils.rset(opts, 'plugins.legend.display', false)
      utils.rset(opts, 'plugins.title.font.size', 11)
      utils.rset(opts, 'plugins.title.padding.bottom', 2)
      utils.rset(opts, 'plugins.tooltip.enabled', false)
      utils.rset(opts, 'scales.x.display', false)
      utils.rset(opts, 'scales.y.display', false)
      utils.rset(opts, 'scales.y.min', 0)
    }
    return opts
  }

  // On Mounted
  // Fetch monthly spending data
  onMounted(function() { updateMonthlySpending() })
  watch(search, function() { updateMonthlySpending() })

  // Update Monthly Spending
  // Fetch monthly spending data from the API
  const updateMonthlySpending = async function() {
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search: search.value || '', months: props.months}
      var {data} = await api.Budget.monthlySpending(params, cancelctrl.signal)
      monthlyData.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw err }
    }
  }
</script>
