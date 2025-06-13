import {utils} from '@/utils'

// Markdown TOC plugin
// Adds IDs to headings and collects them for a table of contents
export default function(md, opts) {
  md.core.ruler.push('add_heading_ids', function(state) {
    state.tokens.forEach(function(token, idx) {
      state.env.headings = state.env.headings || []
      if (token.type === 'heading_open') {
        const text = state.tokens[idx+1].content
        const id = utils.slug(text)
        token.attrs = token.attrs || []
        token.attrs.push(['id', id])
        state.env.headings.push({id:`#${id}`, text:text, tag:token.tag})
      }
    })
  })
}
