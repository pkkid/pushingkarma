import {utils} from '@/utils'

// Inline Image
// ![AltText](image/url.png)
// ![AltText|100x200](image/url.png)
// ![AltText|100](image/url.png)
// https://help.obsidian.md/syntax#External+images
function inlineImage(md, state, silent) {
  const regex = /!\[([^\]|]*)(?:\|(\d+)(?:x(\d+))?)?\]\(([^)]+)\)/y
  regex.lastIndex = state.pos
  const match = regex.exec(state.src)
  if (!match) { return false }
  if (!silent) {
    const alt = md.utils.escapeHtml(match[1].trim())
    const width = match[2].trim()
    const height = match[3].trim()
    const src = utils.obsidianStaticUrl(match[4].trim())
    const style = (width ? `width:${width}px;` : '')
      + (height ? `height:${height}px;` : '')
    const html = `<img src='${src}' alt='${alt}' style='${style}' />`
    state.push('html_inline', '', 0).content = html
  }
  state.pos += match[0].length
  return true  // rule successfully matched
}

// Markdown Image Plugin
// Adds support for Obsidian-style images with optional size in Markdown
export default function markdownImage(md) {
  md.inline.ruler.before('emphasis', 'markdownImage', function(state, silent) {
    return inlineImage(md, state, silent)
  })
}
