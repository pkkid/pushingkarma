import {CodeEditor} from '@/components'
import {utils} from '@/utils'
export var components = {}

// Wrap Code Renderer
// wraps code with div for styling
const wrapCodeRenderer = function(renderer) {
  return function wrappedRenderer(...args) {
    const [tokens, idx] = args
    const token = tokens[idx]
    const component = {
      component: CodeEditor,
      props: {
        value: token.content.trim(),
        language: token.info?.trim() || 'plaintext',
        showlinenums: true,
        isReadonly: true,
      },
    }
    const id = utils.hashObject(component.props)
    components[id] = component
    return `<div class='vue-component' data-id='${id}'></div>`
  }
}

// Markdown HLJS plugin
// markdownIt plugin to add hljs styles
export default function(md, opts) {
  components = {}  // reset for each render
  md.renderer.rules.fence = wrapCodeRenderer(md.renderer.rules.fence)
  md.renderer.rules.code_block = wrapCodeRenderer(md.renderer.rules.code_block)
}
