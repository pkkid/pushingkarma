import {BannerImage} from '@/components'
import {utils} from '@/utils'
export var components = {}

// Parse Params
// Parses params block state.src
const parseProperties = function(state) {
  if (!state.src.startsWith('---')) { return }
  const endindex = state.src.indexOf('---', 3)
  if (endindex === -1) { return }
  const propstr = state.src.slice(3, endindex).trim()
  state.src = state.src.slice(endindex + 3).replace(/^\s*\n/, '')
  // Parse key value pairs
  const properties = Object.fromEntries(
    propstr.split('\n').map(function(line) {
      const match = line.match(/^([^:]+):\s*(.*)$/)
      if (!match) { return null }
      var [_, key, value] = match
      value = value.replace(/^['"]|['"]$/g, '').trim()
      return [key.trim(), value]
    }).filter(Boolean)
  )
  return properties
}

// Create Banner Image
// Creates the BannerImage component placeholder
const createBannerImage = function(params, state) {
  var banner = params.banner.replace(/^\[+/, '').replace(/\]+$/, '')
  banner = utils.obsidianStaticUrl(banner)
  var y = Number(params.banner_y || 0)
  const component = {
    component: BannerImage,
    props: {banner, y}
  }
  const id = utils.hashObject(component.props)
  components[id] = component
  state.src = `<div class='mdvuecomponent' data-id='${id}'></div>\n\n${state.src}`
}


// Markdown Plugin
// Reads paramters from the front of the markdown file
export default function(md, opts) {
  md.core.ruler.before('normalize', 'markdownProps', function(state) {
    components = {}  // reset for each render
    const properties = parseProperties(state)
    for (const key in properties) {
      if (key == 'banner') { createBannerImage(properties, state) }
    }
  })
}
