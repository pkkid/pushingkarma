
// Color Scheme
export const COLORS = {
  RED: '#cc241d',
  ORANGE: '#d65d0e',
  YELLOW: '#d79921',
  GREEN: '#98971a',
  BLUE: '#458588',
  ORANGE_FILL: '#d65d0e33',
  BLUE_FILL: '#45858833',
  GREEN_FILL: '#98971a33',
}

// Base Line Chart Options
// Defaults for all stat line charts.
export const LINEOPTS = {
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {legend: {display: false}, tooltip: {enabled: false}},
  scales: {x: {display: false}, y: {display: false, min: 0}},
  elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 2.5}},
}

// Base Bar Chart Options
// Defaults for bar charts (e.g. per-core CPU bars).
export const BAROPTS = {
  animation: {duration: 300},
  responsive: true,
  maintainAspectRatio: false,
  plugins: {legend: {display: false}, tooltip: {enabled: false}},
  scales: {x: {display: false}, y: {display: false, min: 0, max: 100}},
}

// scrollingChartPlugin
// Chart.js plugin for smooth live-data animations. Supports two independent effects:
//
//   animateX — "scroll left" effect as new data arrives. Instead of Chart.js's built-in
//     animation (which redraws all points at once and causes flicker), this clips the
//     canvas to the chart area, translates it right by one step-width, then eases it
//     back to 0 via a RAF loop — so new data appears to slide in from the right.
//   animateY — smoothly tweens the Y axis max to the current data peak, preventing
//     the scale from jumping when large values arrive. Only active when animateYDuration > 0.
//
// The afterUpdate hook auto-triggers both animations on every data update, so no
// manual watch() is needed. Pass the plugin per-chart via the :plugins prop (not
// Chart.register) so each chart gets its own isolated instance.
//
// Usage:
//   const plugin = scrollingChartPlugin({animateXDuration:300, animateXStyle:'ease'})
//   <Line :plugins="[plugin]" />
export function scrollingChartPlugin({animateXDuration=300, animateXStyle='linear',
    animateYDuration=0, animateYStyle='linear', maxy=null} = {}) {
  const plugin = {
    id: 'chartScroll',

    beforeInit(chart) {
      chart._scroll = {offset:0, xrafid:null, yrafid:null, ymax:null, ready:false}
    },

    destroy(chart) {
      if (chart._scroll?.xrafid) { cancelAnimationFrame(chart._scroll.xrafid) }
      if (chart._scroll?.yrafid) { cancelAnimationFrame(chart._scroll.yrafid) }
      if (chart.canvas) { chart.canvas.style.width = ''; chart.canvas.style.marginLeft = '' }
    },

    beforeDatasetsDraw(chart) {
      const offset = chart._scroll?.offset
      if (!offset || !chart.ctx) { return }
      const {ctx, chartArea:{left, top, width, height}} = chart
      ctx.save()
      ctx.beginPath()
      ctx.rect(left, top, width, height)
      ctx.clip()
      ctx.translate(offset, 0)
    },

    afterDatasetsDraw(chart) {
      if (chart._scroll?.offset) { chart.ctx.restore() }
    },

    // Auto-trigger animation after each real data update.
    // mode='none' updates are from animateymax's own chart.update() calls — skip those
    // to avoid a feedback loop. Also skip the very first render (no data "entered").
    afterUpdate(chart, args) {
      if (args?.mode === 'none') { return }
      const sc = chart._scroll
      if (!sc) { return }
      plugin.updateCanvas(chart)
      if (!sc.ready) { sc.ready = true; return }
      plugin.animateX(chart)
      if (animateYDuration > 0) {
        const vals = chart.data?.datasets?.flatMap(d => d.data).filter(v => v != null) || []
        const calcmax = Math.max(...vals, 1)
        plugin.animateY(chart, maxy !== null ? Math.max(calcmax, maxy) : calcmax)
      }
    },

    // Update Canvas
    // Extend the canvas width by one stepwidth and offset it left by the same amount
    // so data exiting the left edge scrolls smoothly out of view (clipped by the
    // .chartwrap overflow:hidden).
    updateCanvas(chart) {
      if (!chart.chartArea || !chart.canvas) { return }
      const count = chart.data.labels?.length || 1
      const stepwidth = chart.chartArea.width / Math.max(count - 1, 1)
      chart.canvas.style.width = `calc(100% + ${stepwidth*2}px)`
      chart.canvas.style.marginLeft = `-${stepwidth*2}px`
    },

    // Animate X
    // Smoothly scroll line chart to the left
    animateX(chart) {
      const sc = chart?._scroll
      if (!sc || !chart.chartArea) { return }
      if (animateXDuration === 0) { sc.offset = 0; return }
      const count = chart.data.labels?.length || 1
      const stepwidth = chart.chartArea.width / Math.max(count - 1, 1)
      sc.offset = Math.max(sc.offset, stepwidth)
      tween(sc, 'xrafid', animateXDuration, animateXStyle, stepwidth, 0,
        (v) => { if (!chart.ctx) return false; sc.offset = v; chart.draw() },
        () => { sc.offset = 0 },
      )
    },

    // Animate Y
    // Smoothly animate the Y axis max from its current value to newmax.
    animateY(chart, newmax) {
      const sc = chart?._scroll
      if (!sc || !chart.scales?.y) { return }
      const frommax = sc.ymax ?? chart.scales.y.max
      if (newmax === frommax) { return }
      sc.ymax = newmax
      if (animateYDuration === 0) { chart.options.scales.y.max = newmax; chart.update('none'); return }
      tween(sc, 'yrafid', animateYDuration, animateYStyle, frommax, newmax,
        (v) => { if (!chart.ctx) return false; chart.options.scales.y.max = v; chart.update('none') },
        () => { sc.ymax = newmax },
      )
    },
  }

  // Ease
  // Shared ease function (smooth acceleration + deceleration)
  function ease(t) { return t < 0.5 ? 2*t*t : -1+(4-2*t)*t }

  // Tween
  // Shared RAF tween — interpolates from→to over duration, calling onTick each frame.
  // onTick can return false to cancel early (e.g. if the chart was destroyed).
  function tween(sc, key, dur, style, from, to, onTick, onDone) {
    if (sc[key]) { cancelAnimationFrame(sc[key]) }
    const easeFn = style === 'linear' ? (t => t) : ease
    const start = performance.now()
    function tick(now) {
      const t = Math.min((now - start) / dur, 1)
      if (onTick(from + (to - from) * easeFn(t)) === false) { sc[key] = null; return }
      sc[key] = t < 1 ? requestAnimationFrame(tick) : (onDone?.(), null)
    }
    sc[key] = requestAnimationFrame(tick)
  }

  return plugin
}
