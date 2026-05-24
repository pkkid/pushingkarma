<template>
  <div v-if='summary' id='budgetsummary'>
    <div class='bignums'>
      <!-- Total Income (only if nonzero) -->
      <div v-if='summary.total_count < 100 && summary.total_income != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_income, 0)}}</div>
        <div class='bignum-label'>Income</div>
      </div>
      <!-- Total Spent -->
      <div v-if='summary.total_count < 100 && summary.total_spent != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_spent, 0)}}</div>
        <div class='bignum-label'>Spent</div>
      </div>
      <!-- Net Amount -->
      <div v-if='summary.total_count < 100 && summary.total_spent != 0 && summary.total_income != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_amount, 0)}}</div>
        <div class='bignum-label'>Total</div>
      </div>
      <!-- Uncategorized (filter button) -->
      <div v-if='summary.uncategorized_count' class='bignum-panel bignum-btn'
          :class='{active: isFilterActive("category=null")}'
          @click='toggleFilter("category=null")'>
        <div class='bignum-num'>{{utils.intComma(summary.uncategorized_count)}}</div>
        <div class='bignum-label'>Uncategorized</div>
      </div>
      <!-- Unapproved (filter button) -->
      <div v-if='summary.unapproved_count' class='bignum-panel bignum-btn'
          :class='{active: isFilterActive("approved=false")}'
          @click='toggleFilter("approved=false")'>
        <div class='bignum-num'>{{utils.intComma(summary.unapproved_count)}}</div>
        <div class='bignum-label'>Unapproved</div>
      </div>
      <!-- Monthly Spending Chart -->
      <div v-if='summary.total_months >= 3 && chartDatasets' class='bignum-panel bignum-btn minichart-wrap'>
        <div ref='minichartEl' class='minichart' :class='{expanded: isExpanded}' @click='openExpanded'>
          <Transition name='chart-fade'>
            <Bar v-if='showChart' :options='chartOptions' :data='chartDatasets'/>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue'
  import {Bar} from 'vue-chartjs'
  import {Chart, registerables} from 'chart.js'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'
  Chart.register(...registerables)

  const props = defineProps({
    summary: {type:Object, default:null},       // Summary data from parent
  })
  var cancelctrl = null                         // Cancel controller for monthly spending
  const isExpanded = ref(false)                 // Whether the chart is expanded
  const showChart = ref(true)                   // Whether the chart is visible (hidden during resize)
  const minichartEl = ref(null)                 // Chart container element (for click-outside close)
  const monthlyData = ref(null)                 // Monthly spending data
  const {search} = useUrlParams({search:{}})    // Search string from URL

  // Open expanded chart
  const openExpanded = function() {
    isExpanded.value = true
  }

  // Close chart only when clicking outside of it
  const onWindowPointerDown = function(evt) {
    if (!isExpanded.value) { return }
    if (minichartEl.value && !minichartEl.value.contains(evt.target)) {
      isExpanded.value = false
    }
  }

  // Is Filter Active
  // Check if the filter token is already in the search string
  const isFilterActive = function(filter) {
    return (search.value || '').split(/\s+/).includes(filter)
  }

  // Toggle Filter
  // Append or remove a filter token from the current search string
  const toggleFilter = function(filter) {
    var parts = (search.value || '').split(/\s+/).filter(p => p)
    var idx = parts.indexOf(filter)
    if (idx >= 0) { parts.splice(idx, 1) }
    else { parts.push(filter) }
    search.value = parts.join(' ') || null
  }

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
  const chartOptions = computed(function() {
    var opts = {}
    utils.rset(opts, 'events', ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'])
    utils.rset(opts, 'animation.duration', 0)
    utils.rset(opts, 'plugins.legend.display', true)
    utils.rset(opts, 'plugins.legend.labels.boxHeight', 7)
    utils.rset(opts, 'plugins.legend.labels.boxWidth', 7)
    utils.rset(opts, 'plugins.legend.position', 'top')
    utils.rset(opts, 'plugins.legend.align', 'end')
    utils.rset(opts, 'plugins.title.align', 'start')
    utils.rset(opts, 'plugins.title.color', 'var(--lightbg-fg1)')
    utils.rset(opts, 'plugins.title.display', true)
    utils.rset(opts, 'plugins.title.font.size', 15)
    utils.rset(opts, 'plugins.title.padding.bottom', -23)
    utils.rset(opts, 'plugins.title.text', 'Monthly Spend')
    utils.rset(opts, 'plugins.tooltip.enabled', true)
    utils.rset(opts, 'plugins.tooltip.mode', 'index')
    utils.rset(opts, 'plugins.tooltip.intersect', false)
    utils.rset(opts, 'onClick', onChartClick)
    utils.rset(opts, 'plugins.tooltip.callbacks.label', function(ctx) {
      return ` ${ctx.dataset.label}: ${utils.usd(ctx.parsed.y, 0)}`
    })
    utils.rset(opts, 'scales.x.display', true)
    utils.rset(opts, 'scales.x.ticks.font.size', 9)
    utils.rset(opts, 'scales.x.ticks.maxTicksLimit', 12)
    utils.rset(opts, 'scales.y.display', true)
    utils.rset(opts, 'scales.y.ticks.font.size', 9)
    utils.rset(opts, 'scales.y.ticks.callback', function(v) { return utils.usd(v, 0, '$', 3) })
    if (!isExpanded.value) {
      utils.rset(opts, 'events', [])
      utils.rset(opts, 'animation.duration', 0)
      utils.rset(opts, 'layout.padding.top', 0)
      utils.rset(opts, 'layout.padding.left', 0)
      utils.rset(opts, 'layout.padding.right', 0)
      utils.rset(opts, 'layout.padding.bottom', 0)
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
  })

  // Hide chart during minichart resize transition, then restore it
  watch(isExpanded, function() {
    showChart.value = false
    setTimeout(function() { showChart.value = true }, 200)
  })

  // On Mounted
  // Fetch monthly spending data and install click-outside listener
  onMounted(function() {
    updateMonthlySpending()
    window.addEventListener('pointerdown', onWindowPointerDown)
  })
  onBeforeUnmount(function() {
    window.removeEventListener('pointerdown', onWindowPointerDown)
  })
  watch(search, function() {
    isExpanded.value = false
    updateMonthlySpending()
  })

  // Update Monthly Spending
  // Fetch monthly spending data from the API
  const updateMonthlySpending = async function() {
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search: search.value || '', months: 24}
      var {data} = await api.Budget.monthlySpending(params, cancelctrl.signal)
      monthlyData.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw err }
    }
  }
</script>

<style>
  #budgetsummary {
    margin-bottom: 15px;
    clear: both;

    .bignums {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 5px;
      flex-wrap: nowrap;
    }

    .bignum-panel {
      align-items: end;
      border-radius: 6px;
      border: 1px solid var(--lightbg-bg2);
      display: flex;
      flex-direction: column;
      height: 60px;
      justify-content: center;
      min-width: 80px;
      padding: 6px 14px;
      user-select: none;
      white-space: nowrap;

      .bignum-num {
        font-size: 18px;
        font-weight: 600;
        color: var(--lightbg-fg1);
        line-height: 1.2;
        text-align: right;
      }
      .bignum-label {
        font-size: 10px;
        color: var(--lightbg-fg4);
        letter-spacing: 0.04em;
        margin-top: 2px;
      }
      &.bignum-btn {
        cursor: pointer;
        transition: all 0.2s ease;
        &:hover {
          background-color: var(--lightbg-bg2);
          border-color: var(--lightbg-bg3);
        }
        &.active {
          border-color: var(--accent);
          box-shadow: inset 0 0 0 1px var(--accent);
          background-color: #f812;
        }
      }
    }

    .minichart-wrap {
      position: relative;
      width: 110px;
      height: 60px;
      flex-shrink: 0;
    }

    .minichart {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      cursor: pointer;
      border-radius: 5px;
      border: 1px solid transparent;
      background-color: transparent;
      padding: 4px;
      box-sizing: border-box;
      transition: all 0.2s ease;
      z-index: 1;
      &.expanded {
        background-color: var(--lightbg-bg1);
        border-color: var(--lightbg-bg3);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15);
        height: 210px;
        padding: 12px;
        top: -2px;
        left: -1px;
        width: 420px;
        z-index: 50;
      }
    }

    .chart-fade-enter-active { transition: opacity 0.15s ease; }
    .chart-fade-leave-active { transition: opacity 0.1s ease; }
    .chart-fade-enter-from, .chart-fade-leave-to { opacity: 0; }
  }
</style>
