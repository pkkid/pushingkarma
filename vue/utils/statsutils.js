import {triggerChartScroll, animateYMax} from '@/utils/chartscroll'


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
export const lineOpts = {
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {legend: {display: false}, tooltip: {enabled: false}},
  scales: {x: {display: false}, y: {display: false, min: 0}},
  elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 2.5}},
}

// Base Bar Chart Options
// Defaults for bar charts (e.g. per-core CPU bars).
export const barOpts = {
  animation: {duration: 300},
  responsive: true,
  maintainAspectRatio: false,
  plugins: {legend: {display: false}, tooltip: {enabled: false}},
  scales: {x: {display: false}, y: {display: false, min: 0, max: 100}},
}

// Scroll Chart
// Apply animation props from widget defineProps then trigger the scroll animation.
// Pass autoYMax=true to auto-compute the Y axis peak from the chart's own dataset
// and animate to it (for auto-scaling charts like network).
// Call inside a watch(..., {flush: 'post'}) callback after any data updates.
export function scrollChart(chart, props, autoYMax=false) {
  if (chart?.$scroll) {
    chart.$scroll.duration = props?.animationDuration || 300
    chart.$scroll.style = props?.animationStyle || 'ease'
  }
  if (autoYMax) {
    const vals = chart?.data?.datasets?.flatMap(d => d.data).filter(v => v != null) || []
    animateYMax(chart, Math.max(...vals, 1))
  }
  triggerChartScroll(chart)
}
