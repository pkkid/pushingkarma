// chartScrollPlugin
// Chart.js plugin that produces a smooth "scroll left" effect as new data arrives.
// Instead of using Chart.js's built-in animation system (which redraws all points
// simultaneously and causes flicker), this plugin:
//   1. Clips drawing to the chart area
//   2. Applies a decreasing translateX offset via its own RAF loop
//   3. Calls chart.draw() each frame (cheap repaint, no data processing)
//
// Usage:
//   Chart.register(chartScrollPlugin)      // register once (de-duped by id)
//   triggerChartScroll(chartRef.value?.chart)   // call after each data update

const chartScrollPlugin = {
  id: 'chartScroll',

  beforeInit(chart) {
    chart.$scroll = {offset: 0, rafId: null}
  },

  destroy(chart) {
    if (chart.$scroll?.rafId) cancelAnimationFrame(chart.$scroll.rafId)
  },

  beforeDatasetsDraw(chart) {
    const offset = chart.$scroll?.offset
    if (!offset) return
    const {ctx, chartArea: {left, top, width, height}} = chart
    ctx.save()
    ctx.beginPath()
    ctx.rect(left, top, width, height)
    ctx.clip()
    ctx.translate(offset, 0)
  },

  afterDatasetsDraw(chart) {
    if (chart.$scroll?.offset) chart.ctx.restore()
  },
}

// triggerChartScroll
// Call this (with flush:'post') after updating chart data. It resets the canvas
// translate to +stepWidth (so new data appears to enter from the right) and
// linearly decays it to 0 over `duration` ms.
export function triggerChartScroll(chart, duration=1800) {
  if (!chart?.$scroll || !chart.chartArea) return
  const count = chart.data.labels?.length || 1
  const stepWidth = chart.chartArea.width / Math.max(count - 1, 1)
  chart.$scroll.offset = stepWidth
  const start = performance.now()
  if (chart.$scroll.rafId) cancelAnimationFrame(chart.$scroll.rafId)
  function tick(now) {
    const t = Math.min((now - start) / duration, 1)
    chart.$scroll.offset = stepWidth * (1 - t)
    chart.draw()
    if (t < 1) {
      chart.$scroll.rafId = requestAnimationFrame(tick)
    } else {
      chart.$scroll.offset = 0
      chart.$scroll.rafId = null
    }
  }
  chart.$scroll.rafId = requestAnimationFrame(tick)
}

export default chartScrollPlugin
