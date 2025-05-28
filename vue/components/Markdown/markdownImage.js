import {utils} from '@/utils'

// Image Style
// Returns the image style string based on matched width and height
const getImageStyle = function(width, height) {
  var style = ''
  if (width) { style += `width:${width}px;` }
  if (height) { style += `height:${height}px;` }
  return style ? ` style='${style}'` : ''
}

// Markdown Image Plugin
// markdownIt plugin to render images in one of the formats:
//  ![AltText](image/url.png)
//  ![AltText|100x200](image/url.png)
//  ![AltText|100](image/url.png)
// https://help.obsidian.md/syntax#External+images
export default function markdownImage(md) {
  const regex = /!\[([^\]|]*)(?:\|(\d+)(?:x(\d+))?)?\]\(([^)]+)\)/y
  md.inline.ruler.before('emphasis', 'markdownImage', function(state, silent) {
    regex.lastIndex = state.pos
    const match = regex.exec(state.src)
    if (!match) { return false }
    if (!silent) {
      const alt = md.utils.escapeHtml(match[1].trim())
      const style = getImageStyle(match[2], match[3])
      const src = utils.obsidianStaticUrl(match[4].trim())
      const html = `<img src='${src}' alt='${alt}' ${style} />`
      state.push('html_inline', '', 0).content = html
    }
    state.pos += match[0].length
    return true
  })
}
