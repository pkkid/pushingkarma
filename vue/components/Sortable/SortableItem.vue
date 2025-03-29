<template>
  <div class='sortableitem' ref='self' :data-itemid='itemid' draggable='true'
    @dragstart='onDragStart' @dragover='onDragOver' @drop='onDrop' @dragend='onDragEnd'>
    <div class='grip' >⋮</div>
    <div class='content' draggable='true' @dragstart='$event.preventDefault()'>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
  import {onMounted, onUnmounted, ref} from 'vue'
  import {sortableState} from '.'

  const props = defineProps({
    itemid: {required:true},              // Unique item id for this Sortable group
  })
  const self = ref(null)                  // Reference to this element

  // On Mounted / Unmounted
  // Created and remove dragenter event listener
  onMounted(function() { document.addEventListener('dragenter', onDragEnter) })
  onUnmounted(function() { document.removeEventListener('dragenter', onDragEnter) })

  // On Drag Start
  // Save the dragitem and tell the browser were moving it
  const onDragStart = function(event) {
    sortableState.group = self.value.closest('.sortable').dataset.group
    console.log('props.itemid', props.itemid)
    sortableState.itemid = props.itemid.toString()
    event.dataTransfer.effectAllowed = 'move'
  }

  // On Drag Over
  // Highlight the top or bottom border of the item we are hovering
  const onDragOver = function(event) {
    // event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    var item = event.target.closest('.sortableitem')
    if (isSameGroup(item)) {
      clearDropIndicators(item)
      const tbox = item.getBoundingClientRect()
      const offset = event.clientY - tbox.top
      if (offset < tbox.height / 2) {
        item.classList.add('dropbefore')
        item.classList.remove('dropafter')
      } else {
        item.classList.add('dropafter')
        item.classList.remove('dropbefore')
      }
    }
  }

  // On Drop
  // Emit an event telling Sortable we have a new drag order
  const onDrop = function(event) {
    event.preventDefault()
    var item = event.target.closest('.sortableitem')
    if (isSameGroup(item)) {
      var newsort = []
      var sortable = item.closest('.sortable')
      var items = sortable.querySelectorAll('.sortableitem')
      for (var i=0; i<items.length; i++) {
        item = items[i]
        var itemid = item.dataset.itemid
        if (item.classList.contains('dropbefore')) { newsort.push(sortableState.itemid) }
        if (itemid != sortableState.itemid) { newsort.push(itemid) }
        if (item.classList.contains('dropafter')) { newsort.push(sortableState.itemid) }
      }
      const newEvent = new CustomEvent('sort', {detail: {group:sortable.dataset.group, sort:newsort}})
      sortable.dispatchEvent(newEvent)
    }
  }

  // On Drag End
  // Clear the dragitem and remove the dragover class
  const onDragEnd = function() {
    sortableState.group = null
    sortableState.itemid = null
    clearDropIndicators()
  }

  // On Drag Enter
  // Detect if dragging outside the container element
  const onDragEnter = function(event) {
    if (!isSameGroup(event.target)) { clearDropIndicators() }
  }

  // Is Same Group
  // Check if the target and container are the Sortable same
  const isSameGroup = function(item) {
    var group = item.closest('.sortable')?.dataset.group
    return group == sortableState.group
  }

  // Clear Drop Indicators
  // Globally remove the dropbefore and dropafter classes
  const clearDropIndicators = function() {
    var items = document.querySelector('.dropbefore, .dropafter')
    if (items) { items.classList.remove('dropbefore', 'dropafter') }
  }
</script>

<style>
  .sortableitem {
    border-top: 1px solid var(--lightbg-bg3);
    position: relative;

    &:first-child { border-top:none; }
    .content:not(:has(.expandable)) { padding:5px 10px 5px 25px; }
    .content:has(.expandable) .expandable-header { padding:5px 10px 5px 25px; }
    .content:has(.expandable) .expandable-content { padding:0px 10px 5px 25px; }

    .grip {
      color: var(--lightbg-fg3);
      cursor: grab;
      display: flex;
      font-size: 20px;
      justify-content: center;
      line-height: 20px;
      position: absolute;
      top: 5px; left: 3px;
      width: 18px; height:22px;
      opacity: 0.5;
      transition: opacity 0.3s ease;
      &:hover { opacity: 1; }
    }
    &.dropbefore::before,
    &.dropafter::before {
      background-color: var(--accent);
      border-radius: 3px;
      content: '';
      display: block;
      height: 3px;
      position: absolute;
      width: calc(100% - 10px);
      z-index: 999;
    }
    &.dropbefore::before { top:-2px; left:5px; }
    &.dropafter::before { bottom:-2px; left:5px; }
    &:first-child.dropbefore::before { top:0px }
    &:last-child.dropafter::before { bottom:0px }
  }
</style>
