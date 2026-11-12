<template>
  <div ref='barEl' class='bookmarks-bar' @dblclick.stop @contextmenu.self.prevent='showContextMenu($event, barRoot)'
    @dragover='onBarDragOver' @drop='drop'>
    <!-- Bookmarks (items that don't fit are hidden and listed in the overflow menu) -->
    <div ref='itemsEl' class='items' @contextmenu.self.prevent='showContextMenu($event, barRoot)'>
      <BookmarkItem v-for='(item, i) in tree' :key='item.id' :item='item' :level='0' :class='{hidden:i >= visibleCount}'/>
    </div>
    <div class='barbtn addbtn' title='Add bookmark' @click='openEditor()'><i class='mdi mdi-plus'/></div>
    <div v-if='overflowItems.length' ref='overflowEl' class='barbtn' :class='{open:openPath[0] === "overflow"}'
      title='More bookmarks' @click='openFolder({id:"overflow"}, 0)' @dragenter='drag.id && scheduleOpen(0, "overflow")'>
      <i class='mdi mdi-chevron-double-right'/>
      <BookmarkMenu v-if='openPath[0] === "overflow"' :items='overflowItems' :level='1' :anchor='overflowEl'/>
    </div>
    <!-- Context menu -->
    <Teleport to='body'>
      <div v-if='ctxmenu' class='bookmark-menu bookmark-ctxmenu' :style='ctxmenu.style' @contextmenu.prevent>
        <div v-if='ctxmenu.item.kind === "link"' class='bookmark' @click='openNewTab(ctxmenu.item)'>Open in new tab</div>
        <div v-if='["folder", "root"].includes(ctxmenu.item.kind)' class='bookmark' @click='openEditor(null, ctxmenu.item.id)'>Add item here...</div>
        <template v-if='ctxmenu.item.kind !== "root"'>
          <div v-if='ctxmenu.item.kind !== "separator"' class='bookmark' @click='openEditor(ctxmenu.item)'>Edit...</div>
          <div class='bookmark' @click='deleteBookmark(ctxmenu.item)'>Delete...</div>
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
  import {askDelete, load, tree, walk} from './bookmarks'

  const {notify} = inject('notify')
  const barEl = ref(null)                           // Bookmarks bar element
  const itemsEl = ref(null)                         // Bar items container element
  const overflowEl = ref(null)                      // Overflow (>>) button element
  const visibleCount = ref(999)                     // Number of bar items that fit in the bar
  const openPath = ref([])                          // Open folder ids by level ([barFolder, subFolder, ...])
  const drag = reactive({id:null, targetId:null, pos:null})  // Current drag and drop state
  const ctxmenu = ref(null)                         // Context menu {item, style}
  const editor = reactive({visible:false, item:null, parent:null})  // Add/edit modal state
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
    window.addEventListener('blur', onWindowBlur)
  })
  onBeforeUnmount(function() {
    resizeObserver.disconnect()
    document.removeEventListener('mousedown', onDocumentMousedown)
    document.removeEventListener('keydown', onDocumentKeydown)
    document.removeEventListener('dragend', endDrag)
    window.removeEventListener('blur', onWindowBlur)
  })
  watch(tree, () => nextTick(measure), {deep:true})

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

  // Open Folder
  // Clicking a folder opens its menu. Clicking it again leaves it open, menus
  // only close when clicking somewhere else.
  const openFolder = function(item, level) {
    clearTimeout(hoverTimer)
    ctxmenu.value = null
    openPath.value = [...openPath.value.slice(0, level), item.id]
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

  // On Window Blur
  // Close menus when focus leaves the page (clicks outside the new tab iframe), but
  // not while dragging since starting a drag can blur the window and we want the
  // open folder to stay open to drop inside it.
  const onWindowBlur = function() {
    if (!drag.id) { closeMenus() }
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
    if (![barEl.value, itemsEl.value].includes(event.target) || !last || !canDropOn(last)) { return }
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
    if (!editor.item) {
      if (await update(api.Bookmarks.createBookmark(data))) { editor.visible = false }
      return
    }
    const changes = {title:data.title, url:data.url}
    if (data.parent !== editor.parent) { changes.parent = data.parent }
    if (await update(api.Bookmarks.updateBookmark(editor.item.id, changes))) { editor.visible = false }
  }

  // Delete Bookmark
  // Ask to confirm deleting the bookmark (and everything inside it for folders)
  const deleteBookmark = function(item) {
    closeMenus()
    askDelete(item)
  }

  provide('bookmarks', {
    openPath, drag, openFolder, hover, unhover, closeMenus, showContextMenu,
    startDrag, endDrag, canDropOn, setDropTarget, clearDropTarget, drop,
  })
</script>

<style>
  .bookmarks-bar {
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
      flex: 0 1 auto;
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
      &.drop-before { border-radius: 0px; box-shadow: inset 2px 0px 0px var(--bookmarks-accent); }
      &.drop-after { border-radius: 0px; box-shadow: inset -2px 0px 0px var(--bookmarks-accent); }
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
      .mdi { line-height: 1; }
    }
    .addbtn { color: var(--darkbg-fg4); font-size: 14px; margin-right: auto; }
  }

  /* Bookmarks shared by the bar and dropdown menus. Links are the <a> itself so
   * the browser drags them natively, and text selection is disabled explicitly
   * (not just inherited) so pressing a bookmark never selects its text. */
  .bookmarks-bar, .bookmark-menu {
    --bookmarks-accent: var(--darkbg-orange1);  /* Drop indicator, same orange accent as the home page */
    -webkit-user-select: none;
    user-select: none;
  }
  .bookmarks-bar .bookmark, .bookmark-menu .bookmark {
    -webkit-user-drag: element;
    -webkit-user-select: none;
    user-select: none;
    align-items: center;
    border-radius: 4px;
    color: inherit;
    cursor: pointer;
    display: flex;
    flex: 0 0 auto;
    gap: 5px;
    overflow: hidden;
    padding: 0px 8px;
    position: relative;
    white-space: nowrap;
    &:hover, &.open { background-color: #fff2; color: var(--darkbg-fg0); }
    text-decoration: none;
    .title { overflow: hidden; text-overflow: ellipsis; -webkit-user-select: none; user-select: none; }
    .mdi { color: var(--darkbg-fg4); font-size: 14px; }
    &.separator { cursor: grab; padding: 0px; }
    &.separator:hover { background-color: transparent; }
    &.separator::after { background-color: #fff3; content: ''; position: absolute; }
    &.dragging { opacity: 0.4; }
    &.drop-into { background-color: #fe801926; outline: 1px solid var(--bookmarks-accent); outline-offset: -1px; }
  }

  /* Dropdown menus (folders, overflow and context menu) */
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
    min-width: 100px;
    overflow-y: auto;
    padding: 4px;
    position: fixed;
    user-select: none;
    z-index: 50;
    .bookmark {
      height: 26px;
      line-height: 26px;
      .title { margin-right: 20px; }
      &.separator { height: 9px; }
      &.separator::after { left: 6px; right: 6px; top: 4px; height: 1px; }
      &.drop-before { border-radius: 0px; box-shadow: inset 0px 2px 0px var(--bookmarks-accent); }
      &.drop-after { border-radius: 0px; box-shadow: inset 0px -2px 0px var(--bookmarks-accent); }
      .chevron { margin-left: auto; padding-left: 10px; }
    }
    .empty { color: var(--darkbg-fg4); font-style: italic; padding: 5px 8px; }
  }
  .bookmark-ctxmenu { min-width: 160px; z-index: 60; }
</style>
