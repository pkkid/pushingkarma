<template>
  <div class='expandable' :class='{expanded}'>
    <div class='expandable-header' @click='expanded=!expanded'>
      <slot name='header' :expanded='expanded'></slot>
      <i class='mdi mdi-chevron-right expand-icon'/>
    </div>
    <Transition name='slide-fade' :style='`--maxheight:${maxheight};`'>
      <div class='expandable-content' :class='{expanded}' v-show='expanded'>
        <slot name='content'></slot>
      </div>
    </Transition>
  </div>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'

  const props = defineProps({
    initexpanded: {default:false},                // Initial expanded state
    maxheight: {default:'250px'},                 // Estimated height of the content
    itemid: {},                                   // Optional itemid included in events
  })
  const expanded = ref(props.initexpanded)        // True when this is expanded
  const emit = defineEmits(['opened', 'closed'])  // Emit expanded event

  // Watch Expanded
  // Emit expanded event when expanded changes
  watchEffect(function() {
    var emitstr = expanded.value ? 'opened' : 'closed'
    emit(emitstr, {expanded:expanded.value, itemid:props.itemid})
  })

  // Define Exposed
  defineExpose({
    itemid: props.itemid,
    open: function() { expanded.value = true },
    close: function() { expanded.value = false },
  })
</script>

<style>
  .expandable {
    background-color: transparent;
    transition: background-color 0.3s ease;
    .expandable-header {
      align-items: center;
      cursor: pointer;
      display: flex;
      .expand-icon {
        font-size: 20px;
        margin-left: auto; 
        opacity: 0.5;
        transition: all 0.3s ease;
      }
      &:hover .expand-icon { opacity:1; }
    }
    &.expanded, &:hover { background-color:#ddddd988; }
    &.expanded .expand-icon { transform:rotate(90deg); opacity:1; }
    .expandable-content { background-color:var(--lightbg-bg0); }
  }
  .sortableitem:has(.grip:hover) .expandable { background-color:#ddddd988; }
</style>
