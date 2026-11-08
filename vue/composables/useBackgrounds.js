import {ref} from 'vue'
import {Main} from '@/utils/api'

// Use Backgrounds
// Singleton composable with the header background images and a description of where
// each was taken. The list is fetched once per page load and shared by every caller.
export default (function() {
  const backgrounds = ref({})   // Background images keyed by filename
  var request = null            // Pending or completed list request

  // Load
  // Fetch the background list once; a failed request is retried on the next call
  function load() {
    if (request) { return request }
    request = Main.listBackgrounds().then(function({data}) {
      backgrounds.value = Object.fromEntries(data.map(bg => [bg.name, bg]))
    }).catch(function(err) {
      request = null
      console.error('Unable to load backgrounds', err)
    })
    return request
  }

  // Describe
  // Where the background image with this filename was taken, if known
  function describe(name) {
    return backgrounds.value[name]?.description || null
  }

  return function useBackgrounds() {
    load()
    return {backgrounds, describe}
  }
})()
