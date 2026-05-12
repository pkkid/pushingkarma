// Stats Widget Utilities
// Shared colors, base chart options, and helpers used across newtab stat widgets.
import {triggerChartScroll} from '@/utils/chartscroll'

// ---- Colors ----
export const BLUE        = 'rgba(69,133,136,0.9)'
export const BLUE_FILL   = 'rgba(69,133,136,0.15)'
export const GREEN       = 'rgba(152,151,26,0.9)'
export const GREEN_FILL  = 'rgba(152,151,26,0.2)'
export const ORANGE      = 'rgba(214,93,14,0.9)'
export const ORANGE_FILL = 'rgba(214,93,14,0.15)'
export const RED         = 'rgba(204,36,29,0.85)'
export const YELLOW      = 'rgba(215,153,33,0.85)'

// Network chart direction aliases
export const UP_COLOR = ORANGE
export const UP_FILL  = ORANGE_FILL
export const DN_COLOR = BLUE
export const DN_FILL  = BLUE_FILL

// ---- Base Chart Options ----
// Sensible defaults for all stat line charts. Widgets can spread and override as needed.
export const lineOpts = {
  animation: false,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {legend: {display: false}, tooltip: {enabled: false}},
  scales: {x: {display: false}, y: {display: false, min: 0}},
  elements: {point: {radius: 0}, line: {tension: 0.3, borderWidth: 2.5}},
}

// Sensible defaults for bar charts (e.g. per-core CPU bars).
export const barOpts = {
  animation: {duration: 300},
  responsive: true,
  maintainAspectRatio: false,
  plugins: {legend: {display: false}, tooltip: {enabled: false}},
  scales: {x: {display: false}, y: {display: false, min: 0, max: 100}},
}

// ---- Chart Scroll Helper ----
// Apply animation props from widget defineProps then trigger the scroll animation.
// Call inside a watch(..., {flush: 'post'}) callback after any data updates.
export function scrollChart(chart, props) {
  if (chart?.$scroll) {
    chart.$scroll.duration = props.animationDuration
    chart.$scroll.style = props.animationStyle
  }
  triggerChartScroll(chart)
}
