<template>
  <div class='expandable'>
    <div class='expandable-header' @click='expanded=!expanded'>
      <slot name='header'></slot>
      <i class='mdi mdi-chevron-right expand'/>
    </div>
    <Transition name='slide-fade' style='--maxheight:100px;'>
      <div class='expandable-content' :class='{expanded}' v-show='expanded'>
        <slot name='content'></slot>
      </div>
    </Transition>
  </div>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'

  const emit = defineEmits(['expanded'])
  const expanded = ref(false)

  watchEffect(function() {
    emit('expanded', expanded.value)
  })

</script>

<style>
  .expandable {
    .expandable-header {
      display: flex;
      align-items: center;
      cursor: pointer;
      .expand {
        font-size: 20px;
        margin-left:auto; 
        opacity: 0.5;
        transition: opacity 0.3s ease;
      }
      &:hover .expand { opacity: 1; }
    }
    .expandable-content {
      background-color: var(--bgcolor);
      border: 1px solid var(--lightbg-bg2);
      /* padding: 5px 10px; */
      border-radius: 4px;
      /* margin: 5px 0px; */
    }
  }
</style>
