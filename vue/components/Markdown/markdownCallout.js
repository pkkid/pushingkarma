import {Expandable} from '@/components'
import {utils} from '@/utils'

function blockCallout(state, startline, endline, silent) {
  const start = state.bMarks[startline] + state.tShift[startline]
  const max = state.eMarks[startline]
  const line = state.src.slice(start, max)

  // Match Obsidian callout: > [!type] optional-title
  const match = /^>\s*\[!([a-zA-Z0-9_-]+)\](.*)/.exec(line)
  if (!match) { return false }

  // Collect following lines that start with '>'
  var content = []
  var nextline = startline + 1
  while (nextline < endline) {
    const nextStart = state.bMarks[nextline] + state.tShift[nextline]
    const nextMax = state.eMarks[nextline]
    const nextlineText = state.src.slice(nextStart, nextMax)
    if (!/^>\s?/.test(nextlineText)) { break }
    content.push(nextlineText.replace(/^>\s?/, ''))
    nextline++
  }
  if (silent) { return true }

  // Create token
  const token = state.push('callout', 'div', 0)
  token.block = true
  token.info = match[1].toLowerCase()
  token.title = match[2].trim()
  token.content = content.join('\n')
  token.map = [startline, nextline]
  state.line = nextline
  return true
}

// Renderer for callout
const wrapCalloutRenderer = function(renderer) {
  return function(tokens, idx, opts, env) {
    const token = tokens[idx]
    const component = {
      component: Expandable,
      props: {
        type: token.info,
        title: token.title,
        content: token.content,
        markdown: true,
      },
    }
    const id = utils.hashObject(component.props)
    env.components = env.components || {}
    env.components[id] = component
    return `<div class='mdvuecomponent' data-id='${id}'></div>`
  }
}

// Markdown Callout Plugin
// Adds support for Obsidian-style callouts using the Exapandable Vue component
export default function(md, opts) {
  md.block.ruler.before('blockquote', 'callout', blockCallout, {alt:['paragraph','reference','blockquote','list']})
  md.renderer.rules.callout = wrapCalloutRenderer(md.renderer.rules.callout)
}
