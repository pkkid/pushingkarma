<template>
  <div v-if='nodata' class='nodata empty'>Data not available</div>
  <div v-else-if='datasets'><Line :options='options' :data='datasets'/></div>
  <div v-else class='loading-chart'><LoadingIcon style='height:30px;'/></div>
</template>

<script setup>
  import {computed} from 'vue'
  import {utils} from '@/utils'
  import {Line} from 'vue-chartjs'
  import {Chart, registerables} from 'chart.js'
  import LoadingIcon from '@/components/LoadingIcon.vue'
  Chart.register(...registerables)

  var chartColors = ['#cc241d','#98971a','#d79921','#458588','#b16286','#689d6a','#d65d0e']
  Chart.defaults.font.color = '#282828aa'
  Chart.defaults.font.family = 'Inter'
  Chart.defaults.font.weight = 'bold'
  Chart.defaults.font.size = 10

  const props = defineProps({
    title: {required:true},    // Chart title
    data: {required:true},     // Data to render
  })

  // DataDict
  // Data Dict with ticker as the key
  const datadict = computed(function() {
    return props.data.datasets.reduce(function(acc, val) {
      acc[val.label] = val
      return acc
    }, {})
  })

  // No Data
  // Check there is data to display
  const nodata = computed(function() {
    if (datasets.value == null) { return false }
    return Object.keys(datasets.value).length === 0
  })

  // Datasets
  // Format the datasets for chart.js
  const datasets = computed(function() {
    if (props.data === null) { return null }  // still loading
    if (props.data instanceof Error) { return {} }  // no data
    var datasets = []
    for (var i=0; i<props.data.datasets.length; i++) {
      datasets.push({
        label: props.data.datasets[i].label,
        data: props.data.datasets[i].rank.map(v => v * -1),
        borderColor: chartColors[i % chartColors.length],
        backgroundColor: chartColors[i % chartColors.length],
      })
    }
    return {labels:props.data.labels, datasets:datasets}
  })

  // Options
  // Long list of chart.js options
  const options = computed(function() {
    var opts = {}
    utils.rset(opts, 'animation.duration', 300)
    utils.rset(opts, 'elements.line.borderWidth', 1.5)
    utils.rset(opts, 'elements.line.tension', 0.4)
    utils.rset(opts, 'elements.point.radius', 0)
    utils.rset(opts, 'maintainAspectRatio', false)
    utils.rset(opts, 'layout.padding.bottom', 30)
    utils.rset(opts, 'layout.padding.left', 10)
    // Title
    utils.rset(opts, 'plugins.title.align', 'start')
    utils.rset(opts, 'plugins.title.color', '#3c3836')
    utils.rset(opts, 'plugins.title.display', true)
    utils.rset(opts, 'plugins.title.font.family', 'Merriweather')
    utils.rset(opts, 'plugins.title.font.size', '16px')
    utils.rset(opts, 'plugins.title.padding.bottom', 10)
    utils.rset(opts, 'plugins.title.text', props.title)
    // Legend
    utils.rset(opts, 'plugins.legend.align', 'end')
    utils.rset(opts, 'plugins.legend.align', 'start')
    utils.rset(opts, 'plugins.legend.display', true)
    utils.rset(opts, 'plugins.legend.labels.boxHeight', 5)
    utils.rset(opts, 'plugins.legend.labels.boxWidth', 5)
    utils.rset(opts, 'plugins.legend.labels.padding', 4.7)
    utils.rset(opts, 'plugins.legend.position', 'right')
    utils.rset(opts, 'plugins.legend.title.display', true)
    utils.rset(opts, 'plugins.legend.title.padding', 5)
    utils.rset(opts, 'plugins.legend.title.text', '')
    // Tooltips
    utils.rset(opts, 'plugins.tooltip.backgroundColor', '#282828')
    utils.rset(opts, 'plugins.tooltip.bodyColor', '#fbf1c7')
    utils.rset(opts, 'plugins.tooltip.bodyFont.family', 'Roboto Mono')
    utils.rset(opts, 'plugins.tooltip.bodyFont.size', 10)
    utils.rset(opts, 'plugins.tooltip.bodyFont.weight', 'bold')
    utils.rset(opts, 'plugins.tooltip.boxHeight', 7)
    utils.rset(opts, 'plugins.tooltip.boxWidth', 7)
    utils.rset(opts, 'plugins.tooltip.intersect', false)
    utils.rset(opts, 'plugins.tooltip.mode', 'index')
    utils.rset(opts, 'plugins.tooltip.position', 'average')
    utils.rset(opts, 'plugins.tooltip.titleColor', '#fbf1c7')
    utils.rset(opts, 'plugins.tooltip.itemSort', function(a, b) {
      if (a.raw > b.raw) { return -1 }
      if (a.raw < b.raw) { return 1 }
      return 0
    })
    utils.rset(opts, 'plugins.tooltip.callbacks.label', function(ctx) {
      var ticker = ctx.dataset.label
      var i = ctx.dataIndex
      var change = utils.round(datadict.value[ticker].change[i], 1)
      return ` ${ticker.padEnd(4, ' ')} ${change.toString().padStart(5, ' ')}%`
    })
    // Scales
    utils.rset(opts, 'scales.x.border.width', 0)
    utils.rset(opts, 'scales.x.grid.display', true)
    utils.rset(opts, 'scales.x.ticks.display', true)
    utils.rset(opts, 'scales.y.border.width', 0)
    utils.rset(opts, 'scales.y.grid.display', false)
    utils.rset(opts, 'scales.y.max', -0.8)
    utils.rset(opts, 'scales.y.ticks.display', false)
    // Highlight line onHover
    utils.rset(opts, 'plugins.legend.onHover', (event, legendItem) => {
      const datasetIndex = legendItem.datasetIndex
      event.chart.data.datasets[datasetIndex].borderWidth = 3
      event.chart.update()
      if (event.chart.tooltip && event.chart.tooltip.opacity !== 0) {
        event.chart.canvas.dispatchEvent(new Event('mouseout')) }
      event.chart._ticker = legendItem.text
      event.chart._labels = props.data.labels
      event.chart._datadict = datadict.value
    })
    utils.rset(opts, 'plugins.legend.onLeave', (event, legendItem) => {
      const datasetIndex = legendItem.datasetIndex
      event.chart.data.datasets[datasetIndex].borderWidth = 1.5
      event.chart.update()
      event.chart._ticker = null
    })
    return opts
  })

  // Annotate Projected Change
  // Display projected changed on the chart.
  const annotateProjectedChange = {
    id: 'annotateProjectedChange',
    afterDraw(chart) {
      if (chart._ticker) {
        // Configure the font
        const ctx = chart.ctx
        const xAxis = chart.scales['x']
        ctx.save()
        ctx.font = 'bold 10px Inter'
        ctx.fillStyle = '#28282877'
        ctx.textAlign = 'center'
        for (let i = 0; i < chart._labels.length; i++) {
          // Calculate projected change
          var change = chart._datadict[chart._ticker].change[i]
          var period = parseInt(chart._labels[i].replace('w', ''))
          var projected = utils.round(change * (period / 52), 1)
          // Draw the text
          var x = xAxis.getPixelForTick(i)
          var y = chart.height - 21
          ctx.fillText(`${projected}%`, x, y)
        }
        // Draw the xAxis title
        ctx.font = 'bold 12px Merriweather'
        var cx = (chart.chartArea.left + chart.chartArea.right) / 2
        ctx.fillText(`${chart._ticker} Projected 52w Change`, cx, chart.height-3)
        ctx.restore()
      }
    }
  }
  Chart.register(annotateProjectedChange)
</script>

<style>
  .nodata,
  .loading-chart {
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>


