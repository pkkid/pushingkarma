<template>
  <div class='commitchart' v-if='chart'>
    <svg :viewBox='`0 0 ${WIDTH} ${HEIGHT}`' role='img' :aria-label='`Commit history, ${chart.total} commits`'>
      <defs>
        <linearGradient id='commitchartfill' x1='0' y1='0' x2='0' y2='1'>
          <stop offset='0' stop-color='#d65d0e' stop-opacity='.22'/>
          <stop offset='1' stop-color='#d65d0e' stop-opacity='0'/>
        </linearGradient>
      </defs>
      <path :d='chart.area' fill='url(#commitchartfill)'/>
      <line :x1='PAD' :y1='HEIGHT - PAD' :x2='WIDTH - PAD' :y2='HEIGHT - PAD' class='axis'/>
      <path :d='chart.line' class='line'/>
      <circle :cx='chart.end[0]' :cy='chart.end[1]' r='3.5' class='end'/>
    </svg>
    <div class='dates'><span>{{chart.first}}</span><span>{{chart.last}}</span></div>
    <div class='stats'>
      <div><b>{{utils.intComma(chart.total)}}</b><span>commits</span></div>
      <div><b>{{utils.intComma(chart.active)}}</b><span>active {{chart.unit}}</span></div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {utils} from '@/utils'

  const props = defineProps({
    commits: {type:Object, default:null},   // Commit counts per day {YYYY-MM-DD: count}
  })
  const WIDTH = 256, HEIGHT = 64, PAD = 4  // SVG viewbox size and inner padding
  const DAY = 86400000                     // Milliseconds in a day

  // Chart
  // Cumulative commits over the life of the project. Commits are grouped by day, week
  // or month depending on how long the project has run. Periods with no commits are
  // dropped so long breaks do not stretch the chart into a flat line.
  const chart = computed(function() {
    var days = Object.keys(props.commits || {}).sort()
    if (!days.length) { return null }
    var span = (new Date(days.at(-1)) - new Date(days[0])) / DAY
    var size = span < 45 ? 1 : span < 240 ? 7 : 30.44
    // Sum commits into buckets keyed by period number
    var buckets = new Map()
    for (var day of days) {
      var key = Math.floor(new Date(day) / DAY / size)
      buckets.set(key, (buckets.get(key) || 0) + props.commits[day])
    }
    var counts = [...buckets.keys()].sort((a, b) => a - b).map(key => buckets.get(key))
    var total = counts.reduce((sum, count) => sum + count, 0)
    // Build the cumulative line, one even step per active period
    var sx = (WIDTH - PAD * 2) / counts.length
    var sy = (HEIGHT - PAD * 2) / total
    var sum = 0, points = [[PAD, HEIGHT - PAD]]
    counts.forEach(function(count, i) {
      sum += count
      points.push([PAD + (i + 1) * sx, HEIGHT - PAD - sum * sy])
    })
    var line = points.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ')
    var end = points.at(-1)
    return {
      line, end, total,
      area: `${line} L${end[0].toFixed(1)} ${HEIGHT - PAD} Z`,
      active: counts.length,
      unit: size === 1 ? 'days' : size === 7 ? 'weeks' : 'months',
      first: formatDay(days[0], span < 240),
      last: formatDay(days.at(-1), span < 240),
    }
  })

  // Format Day
  // Show the full date for short projects, month and year for longer ones
  function formatDay(day, full) {
    var opts = full ? {month:'short', day:'numeric', year:'numeric'} : {month:'short', year:'numeric'}
    return new Date(day).toLocaleDateString('en-US', {...opts, timeZone:'UTC'})
  }
</script>

<style>
  .commitchart {
    margin-top: 16px;
    svg { display:block; height:auto; overflow:visible; width:100%; }
    .axis { stroke: var(--lightbg-bg2); }
    .line { fill:none; stroke:#d65d0e; stroke-linejoin:round; stroke-width:2; }
    .end { fill:#d65d0e; stroke:#fff; stroke-width:1.5; }
    .dates {
      color: var(--lightbg-fg4);
      display: flex;
      font-size: 11px;
      justify-content: space-between;
      margin-top: 4px;
    }
    .stats {
      border-top: 1px solid var(--lightbg-bg1);
      display: grid;
      gap: 14px;
      grid-template-columns: 1fr 1fr;
      margin-top: 14px;
      padding-top: 14px;
      b {
        color: var(--lightbg-fg0);
        display: block;
        font-family: var(--fontfamily-title);
        font-size: 20px;
        font-weight: 400;
        line-height: 1.3;
      }
      span { color:var(--lightbg-fg4); font-size:11.5px; }
    }
  }
</style>
