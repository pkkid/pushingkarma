<template>
  <Teleport to='body'>
    <div ref='self' class='bookmark-menu' :style='style' @contextmenu.self.prevent>
      <BookmarkItem v-for='item in items' :key='item.id' :item='item' :level='level'/>
      <div v-if='!items.length' class='empty'>(empty)</div>
    </div>
  </Teleport>
</template>

<script setup>
  import {nextTick, onMounted, ref, watch} from 'vue'
  import BookmarkItem from './BookmarkItem.vue'

  const self = ref(null)                            // Reference to the menu element
  const style = ref({visibility:'hidden'})          // Fixed position, computed once rendered
  const props = defineProps({
    items: {type:Array, required:true},             // Bookmarks to display in this menu
    level: {type:Number, required:true},            // 1 opens below the bar, 2+ opens to the side
    anchor: {type:Object, required:true},           // Element this menu is attached to
  })

  // On Mounted / Watch Items
  // Position the menu when opened and whenever its contents change
  onMounted(position)
  watch(() => props.items.length, () => nextTick(position))

  // Position
  // Fixed position the menu next to its anchor, keeping it inside the window. Menus
  // from the bar drop down below it, nested menus open to the right (or left if needed).
  function position() {
    const margin = 4
    const anchor = props.anchor.getBoundingClientRect()
    const menu = self.value.getBoundingClientRect()
    var top = props.level === 1 ? anchor.bottom + 2 : anchor.top - 5
    var left = props.level === 1 ? anchor.left : anchor.right + 2
    if (left + menu.width > window.innerWidth - margin) {
      left = props.level === 1 ? window.innerWidth - menu.width - margin : anchor.left - menu.width - 2
    }
    if (props.level > 1 && top + menu.height > window.innerHeight - margin) {
      top = Math.max(margin, window.innerHeight - menu.height - margin)
    }
    const maxHeight = window.innerHeight - top - margin
    style.value = {top:`${top}px`, left:`${Math.max(margin, left)}px`, maxHeight:`${maxHeight}px`}
  }
</script>
