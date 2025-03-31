import {readonly} from 'vue'
import {useStorage} from '@/composables'
import {utils} from '@/utils'
import axios from 'axios'

export default function useApiSettings() {
  const countQueries = useStorage('axios.countqueries', false)
  const logQueries = useStorage('axios.logqueries', false)
  const saveHistory = useStorage('axios.saveHistory', false)
  const history = useStorage('axios.history', null)
  var HISTORY_IGNORES = ['/login']

  // Set Count Queries
  // Includes the Count-Queries header in requests
  function setCountQueries(newval) {
    countQueries.value = newval
    if (newval) { axios.defaults.headers.common['Count-Queries'] = 'true' }
    else { delete axios.defaults.headers.common['Count-Queries'] }
  }

  // Set Log Queries
  // Includes the Log-Queries header in requests
  function setLogQueries(newval) {
    logQueries.value = newval
    if (newval) { axios.defaults.headers.common['Log-Queries'] = 'true' }
    else { delete axios.defaults.headers.common['Log-Queries'] }
  }

  // Set Save History
  // Enable history saving in the axios interceptor
  function setSaveHistory(newval) {
    saveHistory.value = newval
    axios.defaults.saveHistory = newval
    if (newval) { history.value = history.value || [] }
    else { history.value = null } 
  }

  // Save History Item
  // Saves history item to the history array
  async function saveHistoryItem(response) {
    // Create the new history item
    if (!axios.defaults.saveHistory) { return }
    for (const ignore of HISTORY_IGNORES) {
      if (response.config.url.includes(ignore)) { return }
    }
    const datetime = utils.formatDate(new Date(), 'MMM DD h:mm:ssa')
    const status = response.status || response.response?.status || 0
    const method = (response.config.method || 'get').toUpperCase()
    const path = response.config.url
    const data = response.config.data
    const queries = response.headers?.queries || response.response?.headers?.queries || null
    const item = {datetime, status, method, path, data, queries}
    // Remove old duplicates with same status, method, path, and data
    if (history.value && history.value.length) {
      history.value = history.value.filter(function(itm) { 
        return !(itm.status == status && itm.method == method && itm.path == path
          && itm.queries.split('queries')[0] == queries.split('queries')[0]
          && utils.stringify(itm.data) === utils.stringify(data))
      })
    }
    // Add the new item to the beginning
    history.value.unshift(item)
    if (history.length > 100) { history.value = history.value.slice(0, 100) }
  }
  axios.interceptors.response.use(
    response => { saveHistoryItem(response); return response },
    error => { saveHistoryItem(error); return Promise.reject(error) }
  )

  // Apply initial settings to API
  setCountQueries(countQueries.value)
  setLogQueries(logQueries.value)
  setSaveHistory(saveHistory.value)

  // Return reactive values and methods
  return {
    countQueries: readonly(countQueries),
    logQueries: readonly(logQueries),
    saveHistory: readonly(saveHistory),
    history: readonly(history),
    setCountQueries,
    setLogQueries,
    setSaveHistory
  }
}
