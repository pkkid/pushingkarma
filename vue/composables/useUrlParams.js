import {ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'


// Use URL Params
// Creates reactive refs that sync with URL query parameters. I had to combine
// all values into a single object so that I could watch the entire object
// and update the URL only once when any number of the values change.
// params: an Object of {key:type} pairs
export default function useUrlParams(params) {
  const route = useRoute()
  const router = useRouter()
  const refs = {}

  // Has Data
  // Check if a value is empty or falsy
  const hasData = function(key, value) {
    const type = params[key].type || String
    if (type === Array) { return value && value.length >= 1 }
    else if (type === Set) { return value && value.size >= 1 }
    else if (value) { return true }
    return false
  }

  // String to Value
  // Convert a string to a parameter value
  const strToValue = function(str, type) {
    type = type || String
    if (str === null || str === undefined) { return null }
    if (type == Number) { return Number(str) }
    if (type === Boolean) { return ['true', 't', '1'].includes(str.toLowerCase()) }
    if (type === Array) { return str === null ? [] : str.split(',').map(s => s.trim()) }
    if (type === Set) { return str === null ? new Set() : new Set(str.split(',').map(s => s.trim())) }
    if (type == 'MultiSelect') { return str === null ? [] :
      str.split(',').map(function(s) { return {name:s.trim(), code:s.trim()} }) }
    return str
  }

  // Value to String
  // Convert a paramter value to a string
  const valueToStr = function(value, type) {
    type = type || String
    if (value === null || value === undefined) { return null }
    if (type == Number) { return value.toString() }
    if (type === Boolean) { return value.toString() }
    if (type === Array) { return value.join(',') }
    if (type === Set) { return [...value].join(',') }
    if (type == 'MultiSelect') { return value.map(x => x.code).join(',') }
    return value
  }

  // Watch Route.Query
  // Update the Ref object if a parameter changes
  watch(() => route.query, function(newquery) {
    for (let key in refs) {
      var curvalstr = valueToStr(refs[key].value, params[key].type)
      if (curvalstr != newquery[key]) {
        refs[key].value = strToValue(newquery[key], params[key].type)
      }
    }
  })

  // Initialize
  // We intiialize the starting value of refs with values from the URL
  // as well as watch for any changes to the refs and update the URL.
  for (let key in params) {
    var strval = route.query[key] || null
    var value = strToValue(strval, params[key].type)
    refs[key] = ref(value)
    // Watch for changes on the ref()
    // always update all values
    watch(refs[key], async function() {
      var query = {...route.query}
      for (let key in refs) {
        var qvalue = refs[key].value
        if (query[key] == qvalue) { continue }
        if (!hasData(key, qvalue)) { delete query[key] }
        else { query[key] = valueToStr(qvalue, params[key].type) }
      }
      router.push({query})
    })
  }
  return refs
}
