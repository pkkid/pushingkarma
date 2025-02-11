import hljs from 'highlight.js'

// Highlight
// Highlight code blocks
function highlight(md, hljs, ignoreIllegals, code, lang) {
  try {
    var language = lang !== '' ? lang : 'plaintext'
    return hljs.highlight(code, {language, ignoreIllegals}).value
  } catch (err) {
    return md.utils.escapeHtml(code)
  }
}

// Wrap Code Renderer
// wraps code with div for styling
const wrapCodeRenderer = function(renderer) {
  return function wrappedRenderer(...args) {
    const [tokens, idx, options, env, self] = args
    const token = tokens[idx]
    const langName = token.info ? token.info.trim() : 'plaintext'
    const originalRendered = renderer(...args)
    const langLabel = `<label>${langName}</label>`
    return `<div class="code-block">${langLabel}${originalRendered}</div>`
  }
}

// Markdown HLJS plugin
// markdownIt plugin to add hljs styles
export default function(md, opts) {
  hljs.highlightAll()
  md.options.highlight = (highlight).bind(null, md, hljs, false)
  md.renderer.rules.fence = wrapCodeRenderer(md.renderer.rules.fence)
  md.renderer.rules.code_block = wrapCodeRenderer(md.renderer.rules.code_block)
}
