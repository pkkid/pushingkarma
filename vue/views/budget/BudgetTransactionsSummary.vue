<template>
  <div v-if='summary' id='budgetsummary'>
    <div class='bignums'>
      <!-- Total Spent -->
      <div v-if='summary.total_count < 100 && summary.total_spent != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_spent, 0)}}</div>
        <div class='bignum-label'>Spent</div>
      </div>
      <!-- Total Income (only if nonzero) -->
      <div v-if='summary.total_count < 100 && summary.total_income != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_income, 0)}}</div>
        <div class='bignum-label'>Income</div>
      </div>
      <!-- Net Amount -->
      <div v-if='summary.total_count < 100 && summary.total_spent != 0 && summary.total_income != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_amount, 0)}}</div>
        <div class='bignum-label'>Net</div>
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
      <div v-if='chartDatasets' class='bignum-panel bignum-btn minichart-wrap'>
        <div class='minichart' :class='{expanded: isExpanded}'
            @click='isExpanded = true' @mouseleave='isExpanded = false'>
          <Bar :options='chartOptions' :data='chartDatasets'/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed, onMounted, ref, watch} from 'vue'
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
  const monthlyData = ref(null)                 // Monthly spending data
  const {search} = useUrlParams({search:{}})    // Search string from URL

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
        backgroundColor: '#cc241d33',
        borderColor: '#cc241d',
        borderWidth: 1,
        borderRadius: 2,
      }, {
        label: 'Income',
        data: monthlyData.value.income,
        backgroundColor: '#98971a33',
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

  // On Mounted
  // Fetch monthly spending data
  onMounted(function() { updateMonthlySpending() })
  watch(search, function() { updateMonthlySpending() })

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
          background-color: var(--lightbg-bgs);
          border-color: var(--lightbg-bg4);
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
        top: -5px;
        left: -1px;
        width: 420px;
        z-index: 50;
      }
    }
  }
</style>
