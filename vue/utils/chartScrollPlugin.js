// chartScrollPlugin
// Chart.js plugin that produces a smooth "scroll left" effect as new data arrives.
// Instead of using Chart.js's built-in animation system (which redraws all points
// simultaneously and causes flicker), this plugin:
//   1. Clips drawing to the chart area
//   2. Applies a decreasing translateX offset via its own RAF loop
//   3. Calls chart.draw() each frame (cheap repaint, no data processing)
//
// Usage:
//   Chart.register(chartScrollPlugin(300))  // register once with desired duration
//   triggerChartScroll(chartRef.value?.chart)   // call after each data update

function chartScrollPlugin(duration=300) {
  return {
  id: 'chartScroll',

  beforeInit(chart) {
    chart.$scroll = {offset: 0, rafId: null, duration, yRafId: null, yMax: null}
  },

  destroy(chart) {
    if (chart.$scroll?.rafId) cancelAnimationFrame(chart.$scroll.rafId)
    if (chart.$scroll?.yRafId) cancelAnimationFrame(chart.$scroll.yRafId)
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
}

// triggerChartScroll
// Call this (with flush:'post') after updating chart data. It resets the canvas
// translate to +stepWidth (so new data appears to enter from the right) and
// eases it to 0 over the duration configured in chartScrollPlugin().
export function triggerChartScroll(chart) {
  if (!chart?.$scroll || !chart.chartArea) return
  const duration = chart.$scroll.duration ?? 300
  if (duration === 0) { chart.$scroll.offset = 0; return }
  const count = chart.data.labels?.length || 1
  const stepWidth = chart.chartArea.width / Math.max(count - 1, 1)
  chart.$scroll.offset = Math.max(chart.$scroll.offset, stepWidth)
  const start = performance.now()
  if (chart.$scroll.rafId) cancelAnimationFrame(chart.$scroll.rafId)
  function easeInOut(t) { return t < 0.5 ? 2*t*t : -1+(4-2*t)*t }
  const easeFn = (chart.$scroll.style === 'linear') ? (t => t) : easeInOut
  function tick(now) {
    const t = Math.min((now - start) / duration, 1)
    chart.$scroll.offset = stepWidth * (1 - easeFn(t))
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

// animateYMax
// Smoothly animate the Y axis max of a chart from its current value to a new target.
// Call this after updating chart data when the Y axis uses auto-scaling.
export function animateYMax(chart, newMax) {
  if (!chart?.$scroll) return
  const duration = chart.$scroll.duration ?? 300
  const yScale = chart.scales?.y
  if (!yScale) return
  const fromMax = chart.$scroll.yMax ?? yScale.max
  if (newMax === fromMax) return
  chart.$scroll.yMax = newMax
  if (duration === 0) {
    chart.options.scales.y.max = newMax
    chart.update('none')
    return
  }
  const start = performance.now()
  if (chart.$scroll.yRafId) cancelAnimationFrame(chart.$scroll.yRafId)
  function easeInOut(t) { return t < 0.5 ? 2*t*t : -1+(4-2*t)*t }
  const easeFn = (chart.$scroll.style === 'linear') ? (t => t) : easeInOut
  function tick(now) {
    const t = Math.min((now - start) / duration, 1)
    chart.options.scales.y.max = fromMax + (newMax - fromMax) * easeFn(t)
    chart.update('none')
    if (t < 1) {
      chart.$scroll.yRafId = requestAnimationFrame(tick)
    } else {
      chart.$scroll.yMax = newMax
      chart.$scroll.yRafId = null
    }
  }
  chart.$scroll.yRafId = requestAnimationFrame(tick)
}
