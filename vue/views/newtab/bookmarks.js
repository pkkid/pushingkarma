// Bookmarks
// Shared bookmarks state for the bookmarks bar and the F1 quick search panel
import {ref} from 'vue'
import {api} from '@/utils'

export const tree = ref([])                         // Nested bookmarks tree from the server
export const confirming = ref(null)                 // Pending delete confirmation {item, title, message}

// Load
// Fetch the bookmarks tree from the server
export const load = async function() {
  const {data} = await api.Bookmarks.listBookmarks()
  tree.value = data
}

// Walk
// Flatten the tree into a list of {item, names, ancestors} for searching and the editor
export const walk = function(items=tree.value, names=[], ancestors=[]) {
  return items.flatMap(item => [{item, names, ancestors}].concat(item.kind === 'folder'
    ? walk(item.children, [...names, item.title], [...ancestors, item.id]) : []))
}

// Hostname
// Return the hostname of a url for search result subtitles
export const hostname = function(url) {
  try { return new URL(url).hostname.replace(/^www\./, '') } catch { return url }
}

// Search
// Links matching every word of the query in their title, url or folder path.
// Returns a list of {item, subtitle} where subtitle is the folder path and hostname.
export const search = function(query, limit=20) {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean)
  if (!words.length) { return [] }
  return walk().filter(n => n.item.kind === 'link').map(n => ({
    item: n.item,
    subtitle: [...n.names, hostname(n.item.url)].filter(Boolean).join(' › '),
    text: [n.item.title, n.item.url, ...n.names].join(' ').toLowerCase(),
  })).filter(r => words.every(word => r.text.includes(word))).slice(0, limit)
}

// Ask Delete
// Open the delete confirmation for a bookmark (see BookmarkDelete.vue)
export const askDelete = function(item) {
  const count = item.kind === 'folder' ? walk(item.children).length : 0
  var message = `Delete the bookmark "${item.title || item.url}"?`
  if (item.kind === 'separator') { message = 'Delete this separator?' }
  if (item.kind === 'folder') { message = `Delete the folder "${item.title}"?` }
  if (count) { message = `Delete the folder "${item.title}" and the ${count} items inside it?` }
  const title = `Delete ${{link:'Bookmark', folder:'Folder', separator:'Separator'}[item.kind]}`
  confirming.value = {item, title, message}
}

// Open Url
// Open a url in this tab, or a new tab when ctrl or cmd is held. Uses window.top so it
// replaces the whole tab when the new tab page is shown in a frame.
export const openUrl = function(url, event) {
  if (event?.ctrlKey || event?.metaKey) {
    window.open(url, '_blank')
  } else {
    window.top.location.href = url
  }
}
