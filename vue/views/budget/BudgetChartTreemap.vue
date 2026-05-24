<template>
  <BudgetChart v-if='chartData' v-slot='{isExpanded, isReady}'>
    <ChartView v-if='isReady' type='treemap' :options='chartOptions(isExpanded)' :data='chartData'/>
  </BudgetChart>
</template>

<script setup>
  import {computed, onMounted, ref, watch} from 'vue'
  import {Chart as ChartView} from 'vue-chartjs'
  import {Chart, registerables} from 'chart.js'
  import {TreemapController, TreemapElement} from 'chartjs-chart-treemap'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'
  import BudgetChart from './BudgetChart.vue'
  Chart.register(...registerables, TreemapController, TreemapElement)

  const props = defineProps({
    months: {type:Number, default:24},
    limit: {type:Number, default:25},
  })
  var cancelctrl = null                         // Cancel controller for treemap requests
  const treemapData = ref(null)                 // Category treemap data from API
  const {search} = useUrlParams({search:{}})    // Search string from URL

  const colorForCategory = function(name) {
    var palette = ['#689d6a', '#458588', '#d79921', '#b16286', '#cc241d', '#83a598', '#98971a', '#d65d0e', '#458588', '#8f3f71']
    var seed = 0
    for (var i = 0; i < (name || '').length; i++) {
      seed = (seed + name.charCodeAt(i)) % 997
    }
    return palette[seed % palette.length]
  }

  const withAlpha = function(hex, alpha) {
    var val = hex.replace('#', '')
    if (val.length !== 6) { return hex }
    var r = parseInt(val.slice(0, 2), 16)
    var g = parseInt(val.slice(2, 4), 16)
    var b = parseInt(val.slice(4, 6), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }

  // Apply category filter token from treemap click
  // Replaces existing category filter tokens, then appends the clicked category
  const applyCategoryFilter = function(category) {
    if (!category) { return }
    var token = `category="${category}"`
    var cleaned = (search.value || '').replace(/\bcategory=(?:"[^"]+"|null)/g, '').replace(/\s+/g, ' ').trim()
    search.value = cleaned ? `${cleaned} ${token}` : token
  }

  // Handle treemap block clicks and update category filter in search
  const onChartClick = function(evt, activeEls, chart) {
    var els = chart.getElementsAtEventForMode(evt, 'nearest', {intersect: true}, false)
    if (!els || !els.length) { return }
    var elm = els[0]
    var raw = chart?.data?.datasets?.[elm.datasetIndex]?.data?.[elm.index]
    var node = raw?._data || {}
    applyCategoryFilter(node.category)
  }

  // Build treemap dataset from category treemap API data
  const chartData = computed(function() {
    var items = treemapData.value?.items || []
    if (!items.length) { return null }
    var tree = items.map(function(item) {
      return {category: item.category, value: item.value, count: item.count}
    })
    return {
      datasets: [{
        label: 'Category Spend',
        tree,
        key: 'value',
        groups: ['category'],
        spacing: 1,
        borderWidth: 1,
        borderColor: 'var(--lightbg-bg3)',
        backgroundColor: function(ctx) {
          var category = ctx.raw?._data?.category || ''
          var color = colorForCategory(category)
          return withAlpha(color, 0.78)
        },
      }],
    }
  })

  // Build chart.js options, switching between mini and expanded modes
  const chartOptions = function(isExpanded) {
    var opts = {}
    utils.rset(opts, 'animation.duration', 0)
    utils.rset(opts, 'maintainAspectRatio', false)
    utils.rset(opts, 'events', ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'])
    utils.rset(opts, 'onClick', onChartClick)
    utils.rset(opts, 'plugins.legend.display', false)
    utils.rset(opts, 'plugins.title.align', 'start')
    utils.rset(opts, 'plugins.title.color', 'var(--lightbg-fg1)')
    utils.rset(opts, 'plugins.title.display', true)
    utils.rset(opts, 'plugins.title.text', 'Category Treemap')
    utils.rset(opts, 'plugins.title.font.size', 14)
    utils.rset(opts, 'plugins.title.padding.bottom', 2)
    utils.rset(opts, 'plugins.tooltip.enabled', true)
    utils.rset(opts, 'plugins.tooltip.callbacks.label', function(ctx) {
      var node = ctx.raw?._data || {}
      var amount = utils.usd(node.value || 0, 0)
      var count = utils.intComma(node.count || 0)
      return `${node.category}: ${amount} (${count})`
    })
    utils.rset(opts, 'plugins.tooltip.callbacks.title', function() { return '' })
    if (!isExpanded) {
      utils.rset(opts, 'events', [])
      utils.rset(opts, 'plugins.title.font.size', 11)
      utils.rset(opts, 'plugins.title.padding.bottom', 0)
      utils.rset(opts, 'plugins.tooltip.enabled', false)
      utils.rset(opts, 'layout.padding.top', 0)
      utils.rset(opts, 'layout.padding.left', 0)
      utils.rset(opts, 'layout.padding.right', 0)
      utils.rset(opts, 'layout.padding.bottom', 0)
    }
    return opts
  }

  // Fetch treemap data once mounted and whenever the search string changes
  onMounted(function() {
    updateCategoryTreemap()
  })
  watch(search, function() {
    updateCategoryTreemap()
  })

  // Update Category Treemap
  // Fetch category treemap values from the API
  const updateCategoryTreemap = async function() {
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search: search.value || '', months: props.months, limit: props.limit}
      var {data} = await api.Budget.categoryTreemap(params, cancelctrl.signal)
      treemapData.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw err }
    }
  }
</script>
