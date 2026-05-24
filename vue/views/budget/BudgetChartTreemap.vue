<template>
  <BudgetChart v-if='hasData' :collapseKey='search' :resetChartOnClick='false' :canFullscreen='props.canFullscreen'
    v-slot='{isExpanded, isFullscreen, isReady}' >
    <ChartView v-if='isReady' type='treemap' :options='chartOptions(isExpanded, isFullscreen)' :data='chartData(isExpanded)'/>
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
    months: {type:Number, default:24},              // Number of months to look back for the treemap (e.g. last 12 months)
    limit: {type:Number, default:25},               // Max number of treemap blocks to show (API limit, not client-side)
    canFullscreen: {type:Boolean, default:false},   // Whether to show the fullscreen expand button (only if treemap has data)
  })
  var cancelctrl = null                             // Cancel controller for treemap requests
  const treemapData = ref(null)                     // Category treemap data from API
  const treemapCountLookup = ref({})               // Lookup map for count data by category+payee
  const {search} = useUrlParams({search:{}})        // Search string from URL

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

  // Darken a hex color by mixing it with black.
  // amount=0.5 means 50% original color + 50% black.
  const mixWithBlack = function(hex, amount=0.5) {
    var val = hex.replace('#', '')
    if (val.length !== 6) { return hex }
    var ratio = Math.max(0, Math.min(1, 1 - amount))
    var r = Math.round(parseInt(val.slice(0, 2), 16) * ratio)
    var g = Math.round(parseInt(val.slice(2, 4), 16) * ratio)
    var b = Math.round(parseInt(val.slice(4, 6), 16) * ratio)
    return `rgb(${r}, ${g}, ${b})`
  }

  // Ellipsize long labels so we do not auto-scale text to fit tiny blocks.
  const ellipsis = function(text, maxlen=20) {
    var str = (text || '').trim()
    if (str.length <= maxlen) { return str }
    return `${str.slice(0, Math.max(1, maxlen - 1)).trim()}…`
  }

  // Apply category and/or payee filter token from treemap click
  // Replaces existing category/payee tokens, then appends clicked category/payee.
  // If exclude=true (Shift+click), prefix tokens with '-' for exclusion.
  const applyCategoryFilter = function(category, payee, exclude=false) {
    if (!category && !payee) { return }
    var prefix = exclude ? '-' : ''
    var tokens = []
    if (category) { tokens.push(`${prefix}category="${category}"`) }
    if (payee) { tokens.push(`${prefix}payee~"${payee}"`) }
    var token = tokens.join(' ')
    var cleaned = (search.value || '')
      .replace(/\b-?category=(?:"[^"]+"|null)/g, '')
      .replace(/\b-?payee~(?:"[^"]+"|null)/g, '')
      .replace(/\s+/g, ' ')
      .trim()
    search.value = cleaned ? `${cleaned} ${token}` : token
  }

  // Handle treemap block clicks and update category filter in search
  const onChartClick = function(evt, activeEls, chart) {
    var els = chart.getElementsAtEventForMode(evt, 'nearest', {intersect: true}, false)
    if (!els || !els.length) { return }
    var elm = els[0]
    var raw = chart?.data?.datasets?.[elm.datasetIndex]?.data?.[elm.index]
    var item = raw?.data || raw?._data || raw || {}
    var exclude = !!(evt?.native?.shiftKey || evt?.shiftKey)
    applyCategoryFilter(item.category, item.payee, exclude)
  }

  // True when there is at least one category to render in the treemap
  const hasData = computed(function() {
    return (treemapData.value?.items || []).length > 0
  })

  // Build treemap dataset from category treemap API data
  const chartData = function(isExpanded) {
    var items = treemapData.value?.items || []
    if (!items.length) { return null }
    
    // Build lookup map for counts since the treemap library doesn't preserve them
    treemapCountLookup.value = {}
    var tree = items.map(function(item) {
      var key = `${item.category}|${item.payee}`
      treemapCountLookup.value[key] = item.count
      return {category: item.category, payee: item.payee, value: item.value}
    })
    return {
      datasets: [{
        borderWidth: isExpanded ? 1 : 1,
        groups: ['category', 'payee'],
        key: 'value',
        label: 'Category Spend',
        spacing: isExpanded ? 1 : 1,
        tree: tree,
        captions: {
          display: isExpanded,
          color: '#222c',
          align: 'left',
          padding: 2,
          font: {size: 9, weight: '600'},
          formatter: (ctx) => ellipsis(ctx.raw?.g || ''),
        },
        labels: {
          align: 'left',
          color: '#222c',
          display: isExpanded,
          font: {size:8, weight:'400'},
          formatter: (ctx) => ellipsis(ctx.raw?._data?.payee || ''),
          overflow: 'cut',
          padding: 2,
          position: 'top',
        },
        backgroundColor: function(ctx) {
          var category = ctx.raw?._data?.category || ''
          var color = colorForCategory(category)
          return withAlpha(color, 0.78)
        },
        borderColor: function(ctx) {
          var category = ctx.raw?._data?.category || ''
          var color = colorForCategory(category)
          return mixWithBlack(color, 0.1)
        },
      }],
    }
  }

  // Build chart.js options, switching between mini and expanded modes
  const chartOptions = function(isExpanded, isFullscreen) {
    var opts = {}
    utils.rset(opts, 'animation.duration', 0)
    utils.rset(opts, 'events', ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'])
    utils.rset(opts, 'maintainAspectRatio', false)
    utils.rset(opts, 'onClick', onChartClick)
    utils.rset(opts, 'plugins.legend.display', false)
    utils.rset(opts, 'plugins.title.align', 'start')
    utils.rset(opts, 'plugins.title.color', 'var(--lightbg-fg1)')
    utils.rset(opts, 'plugins.title.display', true)
    utils.rset(opts, 'plugins.title.font.family', 'Merriweather')
    utils.rset(opts, 'plugins.title.font.size', 14)
    utils.rset(opts, 'plugins.title.padding.bottom', 5)
    utils.rset(opts, 'plugins.title.text', 'Amount By Category')
    utils.rset(opts, 'plugins.tooltip.enabled', true)
    utils.rset(opts, 'plugins.tooltip.callbacks.label', function(ctx) {
      // Get the original data from ctx
      var item = ctx.raw?.data || ctx.raw?._data || {}
      
      // The treemap library doesn't preserve extra properties, so look up the count
      var category = item.category || ''
      var payee = item.payee || ''
      var count = 0
      
      if (payee) {
        // If there's a specific payee, look it up directly
        var key = `${category}|${payee}`
        count = treemapCountLookup.value[key] || 0
      } else {
        // If no payee (category-level node), sum all payees under this category
        for (let key in treemapCountLookup.value) {
          if (key.startsWith(`${category}|`)) {
            count += treemapCountLookup.value[key] || 0
          }
        }
      }
      
      var amount = utils.usd(item.value || 0, 0)
      var countStr = utils.intComma(count)
      var isSubcategory = !!payee
      var title = isSubcategory ? ellipsis(payee, 20) : (category || '')
      return `${title}: ${amount} (${countStr})`
    })
    utils.rset(opts, 'plugins.tooltip.callbacks.title', function() { return '' })
    if (!isExpanded) {
      utils.rset(opts, 'events', [])
      utils.rset(opts, 'plugins.title.font.size', 11)
      utils.rset(opts, 'plugins.title.padding.bottom', 0)
      utils.rset(opts, 'plugins.title.text', 'By Category')
      utils.rset(opts, 'plugins.tooltip.enabled', false)
      utils.rset(opts, 'layout.padding.top', 0)
      utils.rset(opts, 'layout.padding.left', 0)
      utils.rset(opts, 'layout.padding.right', 0)
      utils.rset(opts, 'layout.padding.bottom', 0)
    }
    return opts
  }

  // Fetch treemap data once mounted and whenever the search string changes
  onMounted(function() { updateCategoryTreemap() })
  watch(search, function() { updateCategoryTreemap() })

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
