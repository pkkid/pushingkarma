<template>
  <!-- Links render as the <a> itself so the browser drags the link natively -->
  <component :is='item.kind === "link" ? "a" : "div"' ref='self' class='bookmark' :class='classes'
    :href='item.kind === "link" ? item.url : null' :title='tooltip' draggable='true'
    @click='onClick' @contextmenu.prevent.stop='bm.showContextMenu($event, item)'
    @mouseenter='bm.hover(item, level)' @mouseleave='bm.unhover()'
    @dragstart='onDragStart' @dragover='onDragOver' @dragleave='onDragLeave'
    @drop.stop='onDrop' @dragend='bm.endDrag()'>
    <span v-if='item.kind === "link"' class='title'>{{item.title || item.url}}</span>
    <template v-else-if='item.kind === "folder"'>
      <i class='mdi mdi-folder-outline'/>
      <span class='title'>{{item.title}}</span>
      <i v-if='level > 0' class='mdi mdi-chevron-right chevron'/>
    </template>
    <BookmarkMenu v-if='isOpen' :items='item.children' :level='level + 1' :anchor='self'/>
  </component>
</template>

<script setup>
  import {computed, inject, ref} from 'vue'
  import BookmarkMenu from './BookmarkMenu.vue'

  const bm = inject('bookmarks')                    // Shared bookmarks bar state and actions
  const self = ref(null)                            // Reference to this element
  const props = defineProps({
    item: {type:Object, required:true},             // Bookmark {id, kind, title, url, children}
    level: {type:Number, required:true},            // 0 for the bar, 1+ for dropdown menu depth
  })
  const isOpen = computed(() => props.item.kind === 'folder' && bm.openPath.value[props.level] === props.item.id)
  const tooltip = computed(() => props.item.kind === 'link' ? `${props.item.title}\n${props.item.url}` : null)

  // Classes
  // Item kind, open state and drag and drop indicators
  const classes = computed(function() {
    const drop = bm.drag.targetId === props.item.id ? `drop-${bm.drag.pos}` : null
    return [props.item.kind, drop, {open:isOpen.value, dragging:bm.drag.id === props.item.id}]
  })

  // On Click
  // Toggle folders, close menus when following a link in this tab
  const onClick = function(event) {
    if (props.item.kind === 'folder') {
      bm.toggleFolder(props.item, props.level)
    } else if (props.item.kind === 'link' && !event.ctrlKey && !event.metaKey && !event.shiftKey) {
      bm.closeMenus()
    }
  }

  // On Drag Start
  // Remember which bookmark we are dragging
  const onDragStart = function(event) {
    event.stopPropagation()
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', props.item.url || props.item.title)
    bm.startDrag(props.item)
  }

  // On Drag Over
  // Pick before, after or into (folders only) based on the cursor position. The bar
  // is horizontal so we split on x, dropdown menus are vertical so we split on y.
  const onDragOver = function(event) {
    if (!bm.canDropOn(props.item)) { return }
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    const rect = self.value.getBoundingClientRect()
    const ratio = props.level === 0
      ? (event.clientX - rect.left) / rect.width
      : (event.clientY - rect.top) / rect.height
    var pos = ratio < 0.5 ? 'before' : 'after'
    if (props.item.kind === 'folder' && ratio > 0.25 && ratio < 0.75) { pos = 'into' }
    bm.setDropTarget(props.item, pos, props.level)
  }

  // On Drop
  // Recompute the drop position from the drop event itself, then let the bar move it
  const onDrop = function(event) {
    onDragOver(event)
    bm.drop(event)
  }

  // On Drag Leave
  // Clear the drop indicator when the cursor leaves this item
  const onDragLeave = function(event) {
    if (!self.value.contains(event.relatedTarget)) { bm.clearDropTarget(props.item) }
  }
</script>
