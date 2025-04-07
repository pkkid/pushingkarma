
// Indent New Line
// Inserts new line adding indentation if needed
export function indentNewLine(textarea, tabspaces=2) {
  const text = textarea.value
  const pos = textarea.selectionStart
  const curlinestart = text.lastIndexOf('\n', pos - 1) + 1
  const curline = text.substring(curlinestart, pos)
  var indent = curline.match(/^(\s*)/)[1] || ''
  var lastchar = curline.trim().slice(-1)
  if (lastchar.length && '[{('.includes(lastchar)) {
    indent += ' '.repeat(tabspaces)
  }
  console.log(`lastchar="${lastchar}"  ${'[{('.includes(lastchar)}  indent="${indent}"`)
  document.execCommand('insertText', false, '\n'+indent)
}

// Insert Closing Brace
// Inserts closing brace detenting if needed
export function insertClosingBrace(textarea, brace, tabspaces=2) {
  const text = textarea.value
  const pos = textarea.selectionStart
  const linestart = text.lastIndexOf('\n', pos - 1) + 1
  const curindent = text.substring(linestart, linestart + text.substring(linestart).search(/\S|$/))
  if (text.substring(linestart, pos).trim() === '') {
    const spacesToRemove = Math.min(curindent.length, tabspaces)
    if (spacesToRemove > 0) {
      textarea.setSelectionRange(pos - spacesToRemove, pos)
      document.execCommand('delete')
    }
  } else {
    // Just insert the brace at the current position
    document.execCommand('insertText', false, brace)
  }
}

// Tab Indent & Dedent
// Indent or dedent the current line
export function tabIndent(textarea, shiftkey, tabspaces=2) {
  const tab = ' '.repeat(tabspaces)
  const text = textarea.value
  const selstart = textarea.selectionStart
  const selend = textarea.selectionEnd
  if (selstart != selend) {
    // Text Is Selected
    var newlines
    const firstlinestart = text.lastIndexOf('\n', selstart-1) + 1
    const selectedlines = text.substring(firstlinestart, selend).split('\n')
    if (!shiftkey) {
      newlines = selectedlines.map(function(line) { return tab+line })
    } else {
      newlines = selectedlines.map(line => {
        if (line.startsWith(tab)) { return line.substring(tab.length) }
        const spacesToRemove = Math.min(line.match(/^ */)[0].length, tabspaces)
        return line.substring(spacesToRemove)
      })
    }
    const newselend = firstlinestart + newlines.join('\n').length
    const replacement = newlines.join('\n')
    textarea.setSelectionRange(firstlinestart, selend)
    document.execCommand('insertText', false, replacement)
    textarea.setSelectionRange(firstlinestart, newselend)
  } else {
    // No Selected Text
    if (shiftkey) {
      const linestart = text.lastIndexOf('\n', selstart - 1) + 1
      const curline = text.substring(linestart, selstart)
      const spaces = Math.min(curline.match(/^ */)[0].length, tabspaces)
      if (spaces > 0) {
        textarea.setSelectionRange(linestart, linestart + spaces)
        document.execCommand('delete')
        textarea.setSelectionRange(selstart - spaces, selstart - spaces)
      }
    } else {
      console.log('Adding spaces')
      document.execCommand('insertText', false, ' '.repeat(tabspaces))
    }
  }
}


