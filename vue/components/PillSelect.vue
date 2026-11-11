<template>
  <div class='pillselect' role='group'>
    <button v-for='option in options' :key='option.id' type='button' class='pill'
      :class='{on:modelValue === option.id}' @click='emit("update:modelValue", option.id)'>
      {{option.label}}
    </button>
  </div>
</template>

<script setup>
  // Pill Select
  // Small dark segmented toggle for picking one of a few options. Use with
  // v-model and an options list of {id, label}. Pass aria-label or
  // aria-labelledby to describe the group.
  const emit = defineEmits(['update:modelValue'])
  defineProps({
    modelValue: {required:true},                    // Currently selected option id
    options: {type:Array, required:true},           // List of {id, label} options
  })
</script>

<style>
  .pillselect {
    background-color: var(--darkbg-bgh);
    border-radius: 6px;
    display: flex;
    gap: 2px;
    padding: 2px;
    button.pill {
      background: none;
      border: 0px;
      border-radius: 4px;
      color: var(--darkbg-fg3);
      cursor: pointer;
      font-family: var(--fontfamily-article);
      font-size: 11px;
      font-weight: 500;
      padding: 4px 8px;
      &.on { background-color: #3c3836; color: var(--darkbg-fg0); }
    }
  }
</style>
