import {onUnmounted, reactive, ref, readonly} from 'vue'
import {Main} from '@/utils/api'

// Use Glances
// Singleton composable for fetching and storing Glances data
export default (function() {
  var intervalid = null         // setInterval handle
  var refcount = 0              // Number of active component refs
  var host = null               // Glances API host URL
  var polling = false           // True if actively polling
  const data = ref({history: {}})  // Latest /api/4/all payload, always has history
  const trackers = {}           // Registered history trackers {name: {len, lookup, history}}

  // Start Glances
  // Begin polling the Glances API at the specified host and interval
  function startGlances(_host, _interval=2000) {
    if (polling) { return }
    host = _host
    polling = true
    for (const [name, t] of Object.entries(trackers)) {
      t.history = Array.from({length: t.len}, () => ({time: 0, value: 0}))
      data.value.history[name] = t.history
    }
    update()
    intervalid = setInterval(update, _interval)
  }

  // Stop Glances
  // Stop polling the Glances API and clear stored data
  function stopGlances() {
    polling = false
    clearInterval(intervalid)
    data.value = {history: {}}
  }

  // Update
  // Fetch latest data from Glances API
  async function update() {
    try {
      const res = await Main.getGlances()
      const json = res.data
      const now = Date.now()
      const history = {}
      for (const [name, t] of Object.entries(trackers)) {
        t.history = [...t.history.slice(-(t.len - 1)), {time: now, value: t.lookup(json)}]
        history[name] = t.history
      }
      data.value = {...json, history}
    } catch (err) {
      console.log('Glances Error: ', err)
    }
  }

  // Track History
  // Register a history tracker that auto-populates data.history.<name> on each poll.
  // lookup(data) should return the value to record for each poll.
  function trackHistory(name, len, lookup) {
    const initial = Array.from({length: len}, () => ({time: 0, value: 0}))
    trackers[name] = {len, lookup, history: initial}
    if (!data.value) { data.value = {history: {}} }
    data.value.history[name] = initial
  }

  // Get Max Value
  // Return the maximum value of a tracked history item
  function getMaxValue(trackerName) {
    const tracker = trackers[trackerName]
    if (!tracker) { return 0 }
    return Math.max(...tracker.history.map(item => item.value))
  }

  // Use Glances
  // Composable function to use Glances data in a Vue component
  return function useGlances() {
    refcount += 1
    onUnmounted(function() {
      refcount -= 1
      if (refcount == 0) { stopGlances() }
    })
    return reactive({startGlances, trackHistory, getMaxValue, data:readonly(data)})
  }
})()
