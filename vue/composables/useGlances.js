import {ref, readonly} from 'vue'
import useStorage from './useStorage'

export const HISTORY_MINUTES = 2   // How many minutes of history to display (change me)
const POLL_INTERVAL = 2000         // 2 seconds
const HISTORY_LEN = Math.round((HISTORY_MINUTES * 60 * 1000) / POLL_INTERVAL)

// --- Singleton state ---
const host = useStorage('newtab.glances.host', 'http://192.168.4.253:61208')
const data = ref(null)         // Latest full /api/4/all payload
const error = ref(null)        // Fetch error if any

// Rolling history arrays — pre-filled with zeros so charts show full width immediately
const cpuHistory = ref(Array.from({length: HISTORY_LEN}, () => ({time: 0, value: 0})))
const tempHistory = ref(Array.from({length: HISTORY_LEN}, () => ({time: 0, value: 0})))
const netHistory = ref(Array.from({length: HISTORY_LEN}, () => ({time: 0, sent: 0, recv: 0})))
const gpuHistory = ref(Array.from({length: HISTORY_LEN}, () => ({time: 0, value: 0})))

let polling = false

// Push a value into a capped history array
function pushHistory(arr, entry) {
  arr.value = [...arr.value.slice(-(HISTORY_LEN - 1)), entry]
}

// Aggregate network: sum all non-loopback interfaces
function sumNetwork(networkList) {
  return (networkList || []).reduce(function(acc, iface) {
    if (iface.interface_name === 'lo') return acc
    acc.sent += iface.bytes_sent_rate_per_sec || 0
    acc.recv += iface.bytes_recv_rate_per_sec || 0
    return acc
  }, {sent: 0, recv: 0})
}

async function poll() {
  try {
    const res = await fetch(`${host.value}/api/4/all`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()
    data.value = json
    error.value = null
    const now = Date.now()
    pushHistory(cpuHistory, {time: now, value: json.cpu?.total ?? 0})
    const cpuPkg = (json.sensors || []).find(s => s.label === 'Package id 0')
    pushHistory(tempHistory, {time: now, value: cpuPkg?.value ?? 0})
    const net = sumNetwork(json.network)
    pushHistory(netHistory, {time: now, sent: net.sent, recv: net.recv})
    const gpuPercent = json.gpu?.[0]?.proc ?? null
    pushHistory(gpuHistory, {time: now, value: gpuPercent})
  } catch (e) {
    error.value = e
  }
}

function start() {
  if (polling) return
  polling = true
  poll()
  setInterval(poll, POLL_INTERVAL)
}

export default function useGlances() {
  return {
    host,
    data: readonly(data),
    error: readonly(error),
    cpuHistory: readonly(cpuHistory),
    tempHistory: readonly(tempHistory),
    netHistory: readonly(netHistory),
    gpuHistory: readonly(gpuHistory),
    start,
  }
}
