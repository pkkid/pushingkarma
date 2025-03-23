<template>
  <div class='sortableitem' draggable='true' @dragstart='onDragStart'
      @dragover='onDragOver' @drop='onDrop' @dragend='onDragEnd'>
    <div class='grip' >⋮</div>
    <div class='content' draggable='true' @dragstart='preventDragStart'>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
  var dragitem = null

  // On Drag Start
  // Save the dragitem and tell the browser were moving it
  const onDragStart = function(event) {
    dragitem = event.target
    event.dataTransfer.effectAllowed = 'move'
  }

  // Prevent Drag Start
  // Since we only want to allow dragging by the grip elememt, we catch dragging
  // the content and preventDefault to stop us.
  const preventDragStart = function(event) {
    event.preventDefault()
  }

  // On Drag Over
  // Highlight the top or bottom border of the item we are hovering
  const onDragOver = function(event) {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    const target = event.target.closest('.sortableitem')
    if (target && target !== dragitem) {
      clearDragOverClasses()
      const rect = target.getBoundingClientRect()
      const offsetY = event.clientY - rect.top
      if (offsetY < rect.height / 2) {
        target.classList.add('dragover-before')
        target.classList.remove('dragover-after')
      } else {
        target.classList.add('dragover-after')
        target.classList.remove('dragover-before')
      }
    }
  }

  // On Drop
  // Emit an event telling Sortable we have a new drag order
  const onDrop = function(event) {
    console.log('onDrop')
    event.preventDefault()
  }

  // On Drag End
  // Clear the dragitem and remove the dragover class
  const onDragEnd = function() {
    clearDragOverClasses()
    dragitem = null
  }

  // Clear dragover class
  // Remove the existing dragover-before and dragover-after classes
  const clearDragOverClasses = function() {
    const prevDragOverItem = document.querySelector('.sortableitem.dragover-before, .sortableitem.dragover-after')
    if (prevDragOverItem) {
      prevDragOverItem.classList.remove('dragover-before', 'dragover-after')
    }
  }
</script>

<style>
  .sortableitem {
    border-top: 1px solid var(--lightbg-bg3);
    position: relative; 
    &:first-child { border-top: none; }

    .content {
      padding: 5px 10px 5px 25px;
    }
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
    }
    &.dragover-before::before {
      background-color: var(--accent);
      border-radius: 3px;
      content: '';
      display: block;
      height: 3px;
      position: absolute;
      top: -2px; left:5px;
      width: calc(100% - 10px);
      z-index: 900;
    }
    &.dragover-after::before {
      background-color: var(--accent);
      border-radius: 3px;
      content: '';
      display: block;
      height: 3px;
      position: absolute;
      bottom: -2px; left:5px;
      width: calc(100% - 10px);
      z-index: 900;
    }
  }
</style>
