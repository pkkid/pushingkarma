<template>
  <div class='bookmarks-bar' @dblclick.stop @contextmenu.self.prevent='showContextMenu($event, barRoot)'>
    <!-- Bookmarks (items that don't fit are hidden and listed in the overflow menu) -->
    <div ref='itemsEl' class='items' @dragover='onBarDragOver' @drop='drop'
      @contextmenu.self.prevent='showContextMenu($event, barRoot)'>
      <BookmarkItem v-for='(item, i) in tree' :key='item.id' :item='item' :level='0' :class='{hidden:i >= visibleCount}'/>
    </div>
    <div v-if='overflowItems.length' ref='overflowEl' class='barbtn' :class='{open:openPath[0] === "overflow"}'
      title='More bookmarks' @click='toggleFolder({id:"overflow"}, 0)' @dragenter='drag.id && scheduleOpen(0, "overflow")'>
      <i class='mdi mdi-chevron-double-right'/>
      <BookmarkMenu v-if='openPath[0] === "overflow"' :items='overflowItems' :level='1' :anchor='overflowEl'/>
    </div>
    <!-- Search -->
    <div ref='searchWrapEl' class='search'>
      <i class='mdi mdi-magnify'/>
      <input v-model='query' type='text' placeholder='Search bookmarks' spellcheck='false'
        @focus='openSearch' @input='openSearch' @blur='searchOpen = false' @keydown='onSearchKeydown'/>
    </div>
    <div class='barbtn' title='Add bookmark or folder' @click='openEditor(null, null)'><i class='mdi mdi-plus'/></div>
    <!-- Search results -->
    <Teleport to='body'>
      <div v-if='searchOpen && query.trim()' class='bookmark-menu bookmark-search' :style='searchStyle'>
        <a v-for='(result, i) in results' :key='result.item.id' :href='result.item.url' class='bookmark link'
          :class='{selected:i === selected}' @mouseenter='selected = i' @mousedown.prevent>
          <div class='title'>{{result.item.title || result.item.url}}</div>
          <div class='subtitle'>{{result.subtitle}}</div>
        </a>
        <div v-if='!results.length' class='empty'>No bookmarks found</div>
      </div>
    </Teleport>
    <!-- Context menu -->
    <Teleport to='body'>
      <div v-if='ctxmenu' class='bookmark-menu bookmark-ctxmenu' :style='ctxmenu.style' @contextmenu.prevent>
        <div v-if='ctxmenu.item.kind === "link"' class='bookmark' @click='openNewTab(ctxmenu.item)'>Open in new tab</div>
        <div v-if='["folder", "root"].includes(ctxmenu.item.kind)' class='bookmark' @click='openEditor(null, ctxmenu.item.id)'>Add item here...</div>
        <template v-if='ctxmenu.item.kind !== "root"'>
          <div v-if='ctxmenu.item.kind !== "separator"' class='bookmark' @click='openEditor(ctxmenu.item)'>Edit...</div>
          <div class='bookmark' @click='deleteBookmark(ctxmenu.item)'>Delete</div>
        </template>
      </div>
    </Teleport>
    <BookmarkEditor :visible='editor.visible' :item='editor.item' :parent='editor.parent' :folders='folders'
      @close='editor.visible = false' @save='saveEditor'/>
  </div>
</template>

<script setup>
  import {computed, inject, nextTick, onBeforeUnmount, onMounted, provide, reactive, ref, watch} from 'vue'
  import {api} from '@/utils'
  import BookmarkEditor from './BookmarkEditor.vue'
  import BookmarkItem from './BookmarkItem.vue'
  import BookmarkMenu from './BookmarkMenu.vue'

  const {notify} = inject('notify')
  const tree = ref([])                              // Nested bookmarks tree from the server
  const itemsEl = ref(null)                         // Bar items container element
  const overflowEl = ref(null)                      // Overflow (>>) button element
  const searchWrapEl = ref(null)                    // Search input wrapper element
  const visibleCount = ref(999)                     // Number of bar items that fit in the bar
  const openPath = ref([])                          // Open folder ids by level ([barFolder, subFolder, ...])
  const drag = reactive({id:null, targetId:null, pos:null})  // Current drag and drop state
  const ctxmenu = ref(null)                         // Context menu {item, style}
  const editor = reactive({visible:false, item:null, parent:null})  // Add/edit modal state
  const query = ref('')                             // Search input text
  const searchOpen = ref(false)                     // True when the search results are displayed
  const searchStyle = ref({})                       // Fixed position of the search results
  const selected = ref(0)                           // Highlighted search result index
  var hoverTimer = null                             // Delay opening menus while hovering
  var resizeObserver = null                         // Recalculates overflow when the bar resizes
  const barRoot = {kind:'root', id:null}             // Stand-in for the bar itself in the context menu
  const overflowItems = computed(() => tree.value.slice(visibleCount.value))

  // On Mounted / Before Unmount
  // Load bookmarks and add document listeners to close menus and clean up drags
  onMounted(function() {
    load()
    resizeObserver = new ResizeObserver(measure)
    resizeObserver.observe(itemsEl.value)
    document.addEventListener('mousedown', onDocumentMousedown)
    document.addEventListener('keydown', onDocumentKeydown)
    document.addEventListener('dragend', endDrag)
    window.addEventListener('blur', closeMenus)
  })
  onBeforeUnmount(function() {
    resizeObserver.disconnect()
    document.removeEventListener('mousedown', onDocumentMousedown)
    document.removeEventListener('keydown', onDocumentKeydown)
    document.removeEventListener('dragend', endDrag)
    window.removeEventListener('blur', closeMenus)
  })
  watch(tree, () => nextTick(measure), {deep:true})

  // Load
  // Fetch the bookmarks tree from the server
  const load = async function() {
    const {data} = await api.Bookmarks.listBookmarks()
    tree.value = data
  }

  // Update
  // Run an api request returning the new tree. On failure notify and reload.
  const update = async function(request) {
    try {
      const {data} = await request
      tree.value = data
      return true
    } catch (err) {
      notify('Bookmarks Error', err.response?.data?.message || err.message, 'mdi-alert')
      load()
      return false
    }
  }

  // Measure
  // Count how many bar items fit, the rest are hidden and shown in the overflow menu
  const measure = function() {
    if (!itemsEl.value) { return }
    const right = itemsEl.value.getBoundingClientRect().right
    const children = [...itemsEl.value.children]
    const count = children.findIndex(child => child.getBoundingClientRect().right > right + 0.5)
    visibleCount.value = count === -1 ? children.length : count
  }

  // Locate
  // Find a bookmark by id, returns {item, parent, siblings}
  const locate = function(id, items=tree.value, parent=null) {
    for (const item of items) {
      if (item.id === id) { return {item, parent, siblings:items} }
      const found = item.children?.length && locate(id, item.children, item)
      if (found) { return found }
    }
    return null
  }

  // Contains
  // True if the folder contains the bookmark id at any depth
  const contains = function(folder, id) {
    return folder.children.some(child => child.id === id || (child.kind === 'folder' && contains(child, id)))
  }

  // Walk
  // Flatten the tree into a list of {item, names, ancestors} for searching and the editor
  const walk = function(items=tree.value, names=[], ancestors=[]) {
    return items.flatMap(item => [{item, names, ancestors}].concat(item.kind === 'folder'
      ? walk(item.children, [...names, item.title], [...ancestors, item.id]) : []))
  }

  // Folders
  // All folders with their full path for the editor folder select
  const folders = computed(function() {
    return walk().filter(n => n.item.kind === 'folder').map(n => ({
      id: n.item.id, path: [...n.names, n.item.title].join(' › '), ancestors: n.ancestors,
    }))
  })

  // ------------------------------
  // Menus
  // ------------------------------

  // Toggle Folder
  // Clicking a folder opens its menu, clicking it again closes it
  const toggleFolder = function(item, level) {
    clearTimeout(hoverTimer)
    ctxmenu.value = null
    openPath.value = openPath.value[level] === item.id
      ? openPath.value.slice(0, level)
      : [...openPath.value.slice(0, level), item.id]
  }

  // Hover
  // On the bar, switch menus instantly if one is already open (like a browser).
  // In menus, open or close submenus after a short delay so moving the mouse
  // diagonally into a submenu doesn't close it.
  const hover = function(item, level) {
    clearTimeout(hoverTimer)
    if (ctxmenu.value) { return }
    if (level === 0) {
      if (item.kind === 'folder' && openPath.value.length && openPath.value[0] !== item.id) {
        openPath.value = [item.id]
      }
      return
    }
    hoverTimer = setTimeout(function() {
      openPath.value = [...openPath.value.slice(0, level), ...(item.kind === 'folder' ? [item.id] : [])]
    }, 200)
  }
  const unhover = () => clearTimeout(hoverTimer)

  // Close Menus
  // Close all dropdown menus and the context menu
  const closeMenus = function() {
    clearTimeout(hoverTimer)
    openPath.value = []
    ctxmenu.value = null
  }

  // Show Context Menu
  // Display the edit/delete menu for a bookmark at the mouse position
  const showContextMenu = function(event, item) {
    clearTimeout(hoverTimer)
    const left = Math.min(event.clientX, window.innerWidth - 180)
    const top = Math.min(event.clientY, window.innerHeight - 130)
    ctxmenu.value = {item, style:{left:`${left}px`, top:`${top}px`}}
  }

  // On Document Mousedown / Keydown
  // Close menus when clicking outside of them or pressing escape
  const onDocumentMousedown = function(event) {
    if (!event.target.closest('.bookmark-ctxmenu')) { ctxmenu.value = null }
    if (!event.target.closest('.bookmarks-bar, .bookmark-menu')) { closeMenus() }
  }
  const onDocumentKeydown = function(event) {
    if (event.key === 'Escape') { closeMenus() }
  }

  // ------------------------------
  // Drag and Drop
  // ------------------------------

  // Start Drag / End Drag
  // Track the dragged bookmark id and clear everything when done
  const startDrag = function(item) {
    ctxmenu.value = null
    drag.id = item.id
  }
  const endDrag = function() {
    clearTimeout(hoverTimer)
    Object.assign(drag, {id:null, targetId:null, pos:null})
  }

  // Can Drop On
  // We can drop anywhere except on the dragged bookmark itself or inside it
  const canDropOn = function(item) {
    if (!drag.id || item.id === drag.id) { return false }
    const source = locate(drag.id)?.item
    return Boolean(source) && !(source.kind === 'folder' && contains(source, item.id))
  }

  // Set Drop Target / Clear Drop Target
  // Update the drop indicator. Hovering in the middle of a folder opens it.
  const setDropTarget = function(item, pos, level) {
    if (drag.targetId === item.id && drag.pos === pos) { return }
    drag.targetId = item.id
    drag.pos = pos
    clearTimeout(hoverTimer)
    if (pos === 'into') { scheduleOpen(level, item.id) }
  }
  const clearDropTarget = function(item) {
    if (drag.targetId === item.id) { Object.assign(drag, {targetId:null, pos:null}) }
  }

  // Schedule Open
  // Open the folder at level after a short delay while dragging over it
  const scheduleOpen = function(level, id) {
    clearTimeout(hoverTimer)
    hoverTimer = setTimeout(function() {
      if (openPath.value[level] !== id) { openPath.value = [...openPath.value.slice(0, level), id] }
    }, 500)
  }

  // On Bar Drag Over
  // Dragging over the empty space at the end of the bar drops after the last item
  const onBarDragOver = function(event) {
    const last = tree.value[Math.min(visibleCount.value, tree.value.length) - 1]
    if (event.target !== itemsEl.value || !last || !canDropOn(last)) { return }
    event.preventDefault()
    setDropTarget(last, 'after', 0)
  }

  // Drop
  // Move the dragged bookmark locally so the bar updates instantly, then save it.
  // The index is the position within the destination after removing the dragged item.
  const drop = async function(event) {
    event.preventDefault()
    const {id, targetId, pos} = drag
    endDrag()
    if (!id || !targetId) { return }
    const source = locate(id)
    const target = locate(targetId)
    var parent = target.item.id
    var index = target.item.children?.filter(child => child.id !== id).length
    if (pos !== 'into') {
      parent = target.parent?.id ?? null
      index = target.siblings.filter(s => s.id !== id).indexOf(target.item) + (pos === 'after' ? 1 : 0)
    }
    source.siblings.splice(source.siblings.indexOf(source.item), 1)
    const destination = parent === null ? tree.value : locate(parent).item.children
    destination.splice(index, 0, source.item)
    await update(api.Bookmarks.moveBookmark(id, {parent, index}))
  }

  // ------------------------------
  // Search
  // ------------------------------

  // Results
  // Links matching every word of the query in their title, url or folder path
  const results = computed(function() {
    const words = query.value.toLowerCase().split(/\s+/).filter(Boolean)
    if (!words.length) { return [] }
    return walk().filter(n => n.item.kind === 'link').map(n => ({
      item: n.item,
      subtitle: [...n.names, hostname(n.item.url)].filter(Boolean).join(' › '),
      text: [n.item.title, n.item.url, ...n.names].join(' ').toLowerCase(),
    })).filter(r => words.every(word => r.text.includes(word))).slice(0, 20)
  })

  // Hostname
  // Return the hostname of a url for search result subtitles
  const hostname = function(url) {
    try { return new URL(url).hostname.replace(/^www\./, '') } catch { return url }
  }

  // Open Search
  // Show the results dropdown below the search input
  const openSearch = function() {
    closeMenus()
    const rect = searchWrapEl.value.getBoundingClientRect()
    searchStyle.value = {top:`${rect.bottom + 2}px`, right:`${window.innerWidth - rect.right}px`}
    searchOpen.value = true
    selected.value = 0
  }

  // On Search Keydown
  // Arrow keys select a result, enter opens it (ctrl+enter in a new tab), escape clears
  const onSearchKeydown = function(event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      selected.value = Math.min(selected.value + 1, results.value.length - 1)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      selected.value = Math.max(selected.value - 1, 0)
    } else if (event.key === 'Enter' && results.value[selected.value]) {
      const url = results.value[selected.value].item.url
      if (event.ctrlKey || event.metaKey) { window.open(url, '_blank') } else { window.location.href = url }
    } else if (event.key === 'Escape') {
      query.value = ''
      event.target.blur()
    }
  }

  // ------------------------------
  // Add, Edit, Delete
  // ------------------------------

  // Open New Tab
  // Open a link from the context menu in a new tab
  const openNewTab = function(item) {
    window.open(item.url, '_blank')
    closeMenus()
  }

  // Open Editor
  // Open the add/edit modal. When editing, parent is the bookmark's current folder.
  const openEditor = function(item, parent=null) {
    closeMenus()
    editor.item = item
    editor.parent = item ? (locate(item.id).parent?.id ?? null) : parent
    editor.visible = true
  }

  // Save Editor
  // Create or update the bookmark (only send parent when it changed so it isn't moved)
  const saveEditor = async function(data) {
    var request = api.Bookmarks.createBookmark(data)
    if (editor.item) {
      const changes = {title:data.title, url:data.url}
      if (data.parent !== editor.parent) { changes.parent = data.parent }
      request = api.Bookmarks.updateBookmark(editor.item.id, changes)
    }
    if (await update(request)) { editor.visible = false }
  }

  // Delete Bookmark
  // Confirm, then delete the bookmark (and everything inside it for folders)
  const deleteBookmark = async function(item) {
    closeMenus()
    const count = item.kind === 'folder' ? walk(item.children).length : 0
    var message = `Delete the bookmark "${item.title || item.url}"?`
    if (item.kind === 'separator') { message = 'Delete this separator?' }
    if (item.kind === 'folder') { message = `Delete the folder "${item.title}"?` }
    if (count) { message = `Delete the folder "${item.title}" and the ${count} items inside it?` }
    if (!window.confirm(message)) { return }
    await update(api.Bookmarks.deleteBookmark(item.id))
  }

  provide('bookmarks', {
    openPath, drag, toggleFolder, hover, unhover, closeMenus, showContextMenu,
    startDrag, endDrag, canDropOn, setDropTarget, clearDropTarget, drop,
  })
</script>

<style>
  .bookmarks-bar {
    --bookmarks-accent: var(--darkbg-blue1);
    align-items: center;
    background-color: var(--darkbg-bgh);
    border-bottom: 1px solid #0006;
    color: var(--darkbg-fg3);
    display: flex;
    flex: 0 0 auto;
    font-family: var(--fontfamily-article);
    font-size: 11px;
    gap: 2px;
    height: 30px;
    padding: 0px 6px;
    width: 100vw;
    z-index: 20;
    .items {
      align-items: center;
      display: flex;
      flex: 1;
      gap: 2px;
      height: 100%;
      min-width: 0px;
      overflow: hidden;
    }
    .bookmark {
      height: 24px;
      line-height: 24px;
      max-width: 160px;
      &.hidden { visibility: hidden; }
      &.separator { width: 9px; }
      &.separator::after { left: 4px; top: 5px; height: 14px; width: 1px; }
      &.drop-before { box-shadow: inset 2px 0px 0px var(--bookmarks-accent); }
      &.drop-after { box-shadow: inset -2px 0px 0px var(--bookmarks-accent); }
    }
    .barbtn {
      align-items: center;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      flex: 0 0 auto;
      font-size: 16px;
      height: 24px;
      justify-content: center;
      width: 24px;
      &:hover, &.open { background-color: #fff2; color: var(--darkbg-fg0); }
    }
    .search {
      margin-left: 6px;
      position: relative;
      .mdi {
        color: var(--darkbg-fg4);
        font-size: 14px;
        left: 6px;
        line-height: 1;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        &::before { line-height: 1; }
      }
      input {
        background-color: #fff1;
        border: 1px solid #fff1;
        border-radius: 4px;
        box-shadow: none;
        color: var(--darkbg-fg1);
        font-family: var(--fontfamily-article);
        font-size: 11px;
        height: 22px;
        padding: 0px 8px 0px 24px;
        transition: width 0.2s ease, border-color 0.2s ease;
        width: 170px;
        &::placeholder { color: var(--darkbg-fg4); }
        &:focus { background-color: #fff1; border-color: var(--bookmarks-accent); box-shadow: none; width: 240px; }
      }
    }
  }

  /* Bookmarks shared by the bar and dropdown menus */
  .bookmarks-bar .bookmark, .bookmark-menu .bookmark {
    align-items: center;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    flex: 0 0 auto;
    gap: 5px;
    overflow: hidden;
    padding: 0px 8px;
    position: relative;
    white-space: nowrap;
    &:hover, &.open { background-color: #fff2; color: var(--darkbg-fg0); }
    &.link { padding: 0px; }
    a, a:visited {
      color: inherit;
      display: block;
      height: 100%;
      line-height: inherit;
      overflow: hidden;
      padding: 0px 8px;
      text-decoration: none;
      text-overflow: ellipsis;
      width: 100%;
    }
    .title { overflow: hidden; text-overflow: ellipsis; }
    .mdi { color: var(--darkbg-fg4); font-size: 14px; }
    &.separator { cursor: grab; padding: 0px; }
    &.separator:hover { background-color: transparent; }
    &.separator::after { background-color: #fff3; content: ''; position: absolute; }
    &.dragging { opacity: 0.4; }
    &.drop-into { background-color: #83a59840; outline: 1px solid var(--darkbg-blue1); outline-offset: -1px; }
  }

  /* Dropdown menus (folders, overflow, search results and context menu) */
  .bookmark-menu {
    background-color: var(--darkbg-bg0);
    border: 1px solid #fff2;
    border-radius: 6px;
    box-shadow: 0px 6px 20px #000a;
    color: var(--darkbg-fg3);
    display: flex;
    flex-direction: column;
    font-family: var(--fontfamily-article);
    font-size: 11px;
    max-width: 340px;
    min-width: 200px;
    overflow-y: auto;
    padding: 4px;
    position: fixed;
    user-select: none;
    z-index: 50;
    .bookmark {
      height: 26px;
      line-height: 26px;
      &.separator { height: 9px; }
      &.separator::after { left: 6px; right: 6px; top: 4px; height: 1px; }
      &.drop-before { box-shadow: inset 0px 2px 0px var(--darkbg-blue1); }
      &.drop-after { box-shadow: inset 0px -2px 0px var(--darkbg-blue1); }
      .chevron { margin-left: auto; padding-left: 10px; }
    }
    .empty { color: var(--darkbg-fg4); font-style: italic; padding: 5px 8px; }
  }
  .bookmark-search {
    max-height: 70vh;
    width: 360px;
    .bookmark.link, .bookmark.link:visited {
      align-items: flex-start;
      color: inherit;
      line-height: 16px;
      flex-direction: column;
      gap: 0px;
      height: auto;
      justify-content: center;
      padding: 4px 8px;
      text-decoration: none;
      &:hover { background-color: transparent; }
      &.selected { background-color: #fff2; color: var(--darkbg-fg0); }
      .title, .subtitle { max-width: 100%; overflow: hidden; text-overflow: ellipsis; }
      .subtitle { color: var(--darkbg-fg4); font-size: 10px; }
    }
  }
  .bookmark-ctxmenu { min-width: 160px; z-index: 60; }
</style>
