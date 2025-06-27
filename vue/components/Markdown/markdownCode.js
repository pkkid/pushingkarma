import {CodeEditor} from '@/components'
import {Gallery} from '@/components/Gallery'
import {utils} from '@/utils'
import yaml from 'js-yaml'

// Wrap Code Renderer
// wraps code with div for styling
const wrapCodeRenderer = function(renderer) {
  return function wrappedRenderer(tokens, idx, opts, env) {
    const token = tokens[idx]
    const language = token.info?.trim() || 'plaintext'
    const content = token.content.trim()
    var component = {}
    if (language == 'img-gallery') {
      // Gallery Component
      component.component = Gallery
      component.props = yaml.load(content)
    } else {
      // CodeEditor Component
      component.component = CodeEditor
      component.props = {
        value: content,
        language: language,
        showlinenums: true,
        isReadonly: true,
      }
    }
    const id = utils.hashObject(component.props)
    env.components = env.components || {}
    env.components[id] = component
    return `<div class='mdvuecomponent' data-id='${id}'></div>`
  }
}

// Markdown Code Plugin
// Overrides the default fence and code_block renderers
export default function(md, opts) {
  md.renderer.rules.fence = wrapCodeRenderer(md.renderer.rules.fence)
  md.renderer.rules.code_block = wrapCodeRenderer(md.renderer.rules.code_block)
}
