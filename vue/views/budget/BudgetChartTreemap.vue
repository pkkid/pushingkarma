<template>
  <BudgetChart v-if='hasData' :collapseKey='search' :resetChartOnClick='false' :canFullscreen='props.canFullscreen'
    v-slot='{isExpanded, isFullscreen, isReady}'>
    <div class='treemap-content' :class='{expanded: isExpanded}'>
      <ChartView v-if='isReady' type='treemap' :options='chartOptions(isExpanded, isFullscreen)' :data='chartData(isExpanded)'/>
      <div v-if='isExpanded' class='subtext treemap-subtext'><i>Click to filter by category or payee. Shift+Click to exclude.</i></div>
    </div>
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

  // On Mounted  and Watch Search
  // Fetch treemap data once mounted and whenever the search string changes
  onMounted(function() { updateCategoryTreemap() })
  watch(search, function() { updateCategoryTreemap() })

  // Color For Category
  // Get a consistent color for a category name by hashing it to a palette
  const getColor = function(name) {
    var palette = ['#689d6a','#458588','#d79921','#b16286','#cc241d',
      '#83a598','#98971a','#d65d0e','#458588','#8f3f71']
    var seed = 0
    for (var i = 0; i < (name || '').length; i++) {
      seed = (seed + name.charCodeAt(i)) % 997
    }
    return palette[seed % palette.length]
  }

  // With Alpha
  // Add alpha transparency to a hex color (e.g. for hover states)
  const withAlpha = function(hex, alpha) {
    var val = hex.replace('#', '')
    if (val.length !== 6) { return hex }
    var r = parseInt(val.slice(0, 2), 16)
    var g = parseInt(val.slice(2, 4), 16)
    var b = parseInt(val.slice(4, 6), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }

  // Mix With Black
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

  // Ellipsize
  // Ellipsize long labels so we do not auto-scale text to fit tiny blocks.
  const ellipsis = function(text, maxlen=20) {
    var str = (text || '').trim()
    if (str.length <= maxlen) { return str }
    return `${str.slice(0, Math.max(1, maxlen - 1)).trim()}…`
  }

  // Get Item Count
  // Get count for item from lookup by category and optional payee
  const getItemCount = function(category, payee) {
    if (payee && category) {
      return treemapCountLookup.value[`${category}|${payee}`] || 0
    }
    var count = 0
    for (let key in treemapCountLookup.value) {
      var matches = payee ? key.endsWith(`|${payee}`) : key.startsWith(`${category}|`)
      if (matches) { count += treemapCountLookup.value[key] || 0 }
    }
    return count
  }

  // Apply Category Filter
  // Apply category and/or payee filter token from treemap click.
  // Normal click replaces existing category/payee filters.
  // Shift+click appends exclude filters so multiple exclusions can accumulate.
  const applySearchFilter = function(category, payee, exclude=false) {
    var tokens = []
    exclude = exclude ? '-' : ''
    if (exclude && category && payee) { category = '' }    
    if (category) { tokens.push(`${exclude}category="${category}"`) }
    if (payee) { tokens.push(`${exclude}payee~"${payee}"`) }
    // var cleaned = (search.value || '')
    // if (exclude) {
    //   cleaned = cleaned.replace(/(^|\s)category=(?:"[^"]+"|null)(?=\s|$)/g, ' ')
    //   cleaned = cleaned.replace(/(^|\s)payee~(?:"[^"]+"|null)(?=\s|$)/g, ' ')
    // } else {
    //   cleaned = cleaned.replace(/(^|\s)-?category=(?:"[^"]+"|null)(?=\s|$)/g, ' ')
    //   cleaned = cleaned.replace(/(^|\s)-?payee~(?:"[^"]+"|null)(?=\s|$)/g, ' ')
    // }
    // var result = cleaned.replace(/\s+/g, ' ').trim()
    var result = (search.value || '').trim()
    for (const token of tokens) {
      var escaped = token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      var tokenRegex = new RegExp(`(^|\\s)${escaped}(?=\\s|$)`)
      if (!tokenRegex.test(result)) {
        result = result ? `${result} ${token}` : token
      }
    }
    search.value = result || null
  }

  // On Chart Click
  // Handle treemap block clicks and update category filter in search
  const getTreemapItem = function(raw) {
    var merged = Object.assign({}, raw || {}, raw?.data || {}, raw?._data || {})
    var groups = Array.isArray(raw?.gs) ? raw.gs : []
    if (!merged.category && !singleCategory.value && groups[0]) { merged.category = groups[0] }
    if (!merged.payee && groups[1]) { merged.payee = groups[1] }
    if (!merged.payee && singleCategory.value && groups[0]) { merged.payee = groups[0] }
    return merged
  }

  // On Chart Click
  // When a treemap block is clicked, get the associated category and/or
  // payee and update the search filter.
  const onChartClick = function(event, elems, chart) {
    var hits = chart.getElementsAtEventForMode(event, 'point', {intersect: true}, false)
    if (!hits || !hits.length) { return }
    var getHitItem = function(elm) {
      var point = chart?.getDatasetMeta?.(elm.datasetIndex)?.data?.[elm.index]
      var raw = point?.$context?.raw || chart?.data?.datasets?.[elm.datasetIndex]?.data?.[elm.index]
      return getTreemapItem(raw)
    }
    var items = hits.map(getHitItem).filter(Boolean)
    var item = items.find(function(i) { return !!i.payee }) || items[0]
    if (!item) { return }
    var exclude = !!(event?.native?.shiftKey || event?.shiftKey)
    var category = item.category || (singleCategory.value ? treemapData.value?.items?.[0]?.category : '')
    applySearchFilter(category, item.payee, exclude)
  }

  // Has Data
  // True when there is at least one category to render in the treemap
  const hasData = computed(function() {
    return (treemapData.value?.items || []).length > 0
  })

  // Single Category
  // True when all treemap items belong to the same category; in this case
  // we flatten the chart to show payees as top-level blocks instead of nesting them.
  const singleCategory = computed(function() {
    var items = treemapData.value?.items || []
    if (!items.length) { return false }
    var first = items[0].category
    return items.every(function(i) { return i.category === first })
  })

  // Chart Data
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
    // build the dataset
    var ds = {}
    utils.rset(ds, 'borderWidth', 1)
    utils.rset(ds, 'groups', singleCategory.value ? ['payee'] : ['category', 'payee'])
    utils.rset(ds, 'key', 'value')
    utils.rset(ds, 'label', 'Category Spend')
    utils.rset(ds, 'spacing', 1)
    utils.rset(ds, 'tree', tree)
    utils.rset(ds, 'captions.align', 'left')
    utils.rset(ds, 'captions.color', '#222c')
    utils.rset(ds, 'captions.display', isExpanded)
    utils.rset(ds, 'captions.font.size', 10)
    utils.rset(ds, 'captions.font.weight', '600')
    utils.rset(ds, 'captions.formatter', (ctx) => ctx.raw?.g || '')
    utils.rset(ds, 'captions.padding', 2)
    utils.rset(ds, 'labels.align', 'left')
    utils.rset(ds, 'labels.color', '#222c')
    utils.rset(ds, 'labels.display', isExpanded)
    utils.rset(ds, 'labels.font.size', 9)
    utils.rset(ds, 'labels.font.weight', '400')
    utils.rset(ds, 'labels.formatter', (ctx) => ctx.raw?._data?.payee || '')
    utils.rset(ds, 'labels.overflow', 'cut')
    utils.rset(ds, 'labels.padding', 2)
    utils.rset(ds, 'labels.position', 'top')
    utils.rset(ds, 'backgroundColor', function(ctx) {
      var name = singleCategory.value ? (ctx.raw?._data?.payee || '') : (ctx.raw?._data?.category || '')
      return withAlpha(getColor(name), 0.78)
    })
    utils.rset(ds, 'borderColor', function(ctx) {
      var name = singleCategory.value ? (ctx.raw?._data?.payee || '') : (ctx.raw?._data?.category || '')
      return mixWithBlack(getColor(name), 0.1)
    })
    return {datasets: [ds]}
  }

  // Chart Options
  // Build chart.js options, switching between mini and expanded modes
  const chartOptions = function(isExpanded, isFullscreen) {
    var opts = {}
    utils.rset(opts, 'animation.duration', 0)
    utils.rset(opts, 'events', ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'])
    utils.rset(opts, 'layout.padding.bottom', isExpanded ? 16 : 0)
    utils.rset(opts, 'maintainAspectRatio', false)
    utils.rset(opts, 'onClick', onChartClick)
    utils.rset(opts, 'plugins.legend.display', false)
    utils.rset(opts, 'plugins.title.align', 'start')
    utils.rset(opts, 'plugins.title.color', 'var(--lightbg-fg1)')
    utils.rset(opts, 'plugins.title.display', true)
    utils.rset(opts, 'plugins.title.font.family', 'Merriweather')
    utils.rset(opts, 'plugins.title.font.size', 14)
    utils.rset(opts, 'plugins.title.padding.bottom', 5)
    utils.rset(opts, 'plugins.title.text', singleCategory.value ? 'Amount By Payee' : 'Amount By Category')
    utils.rset(opts, 'plugins.tooltip.bodyFont.size', 10)
    utils.rset(opts, 'plugins.tooltip.callbacks.label', function() { return null })
    utils.rset(opts, 'plugins.tooltip.enabled', true)
    utils.rset(opts, 'plugins.tooltip.titleFont.size', 12)
    utils.rset(opts, 'plugins.tooltip.titleMarginBottom', 0)
    utils.rset(opts, 'plugins.tooltip.yAlign', 'top')
    utils.rset(opts, 'plugins.tooltip.callbacks.title', function(items) {
      var item = getTooltipItem(items)
      return item.payee ? ellipsis(item.payee, 20) : ellipsis(item.category, 20)
    })
    utils.rset(opts, 'plugins.tooltip.callbacks.beforeBody', function(items) {
      var item = getTooltipItem(items)
      var count = getItemCount(item.category || '', item.payee || '')
      var amount = utils.usd(item.value || 0, 0)
      var countStr = utils.intComma(count)
      return [`${countStr} transactions`, amount]
    })
    
    if (!isExpanded) {
      utils.rset(opts, 'events', [])
      utils.rset(opts, 'plugins.title.font.size', 11)
      utils.rset(opts, 'plugins.title.padding.bottom', 0)
      utils.rset(opts, 'plugins.title.text', singleCategory.value ? 'By Payee' : 'By Category')
      utils.rset(opts, 'plugins.tooltip.enabled', false)
      utils.rset(opts, 'layout.padding.top', 0)
      utils.rset(opts, 'layout.padding.left', 0)
      utils.rset(opts, 'layout.padding.right', 0)
      utils.rset(opts, 'layout.padding.bottom', 0)
    }
    return opts
  }

  // Get Tooltip Item
  // Get the relevant data item for the tooltip from the list of hovered items.
  const getTooltipItem = function(items) {
    var list = Array.isArray(items) ? items : []
    var payeeItem = list.find(function(item) {
      return (item?.raw?.data?.payee || item?.raw?._data?.payee)
    })
    var targetItem = payeeItem || list[0] || {}
    return targetItem?.raw?.data || targetItem?.raw?._data || {}
  }

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

<style scoped>
  .treemap-content {
    position: relative;
    height: 100%;
    width: 100%;
  }
  .treemap-subtext {
    position: absolute;
    bottom: 0;
    left: 2px;
    z-index: 2;
    line-height: 1.1;
    text-align: left;
    white-space: normal;
    pointer-events: none;
  }
</style>
