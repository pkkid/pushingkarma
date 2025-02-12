import {utils} from '@/utils'

// Saved headings for rendering elsewhere
var markdownHeadings = []

// Markdown TOC plugin
// markdownIt plugin to add heading ids
export default function(md, options) {
  md.core.ruler.push('add_heading_ids', function (state) {
    markdownHeadings = []
    state.tokens.forEach((token, index) => {
      if (token.type === 'heading_open') {
        const text = state.tokens[index+1].content
        const id = utils.slug(text)
        token.attrs = token.attrs || []
        token.attrs.push(['id', id])
        markdownHeadings.push({id:`#${id}`, text:text, tag:token.tag})
      }
    })
  })
}

// Export the saved headings
export {markdownHeadings}
