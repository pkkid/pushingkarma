<template>
  <div class='toggle-switch' :class='{active:currentValue}' @click='onClick'>
    <div class='toggle-track'>
      <div class='toggle-thumb'></div>
    </div>
    <label v-if='label'>{{label}}</label>
  </div>
</template>

<script setup>
  import {ref, watch} from 'vue'

  const props = defineProps({
    modelValue: {type:Boolean, default:undefined},          // Two-way binding
    value: {type:Boolean, default:undefined},               // One-way binding
    label: {type:String, default:''},                       // Toggle label
    width: {type:String, default:'28px'},                   // Width of the toggle
    height: {type:String, default:'16px'},                  // Height of the toggle
  })
  const emit = defineEmits(['update:modelValue', 'update']) // Emit update event
  const currentValue = ref(null)                            // Current value of the toggle

  // Watch Model Value
  // Update currentValue when modelValue changes
  watch(() => props.modelValue, (newval) => {
    if (newval !== currentValue.value) {
      currentValue.value = newval ?? props.value
    }
  }, {immediate: true})

  // Toggle
  // Emit the new value when the toggle is clicked
  const onClick = function() {
    var newval = !currentValue.value
    currentValue.value = newval
    emit('update:modelValue', newval)
    emit('update', newval)
  }
</script>

<style>
.toggle-switch {
  --toggle-width: v-bind(width);
  --toggle-height: v-bind(height);

  align-items: center;
  cursor: pointer;
  display: flex;
  font-size: 12px;
  gap: 8px;
  user-select: none;

  .toggle-track {
    background-color: var(--lightbg-bg4);
    border-radius: 20px;
    height: var(--toggle-height);
    position: relative;
    transition: background-color 0.3s;
    width: var(--toggle-width);
  }

  .toggle-thumb {
    background-color: var(--lightbg-bg0);
    border-radius: 50%;
    height: calc(var(--toggle-height) - 4px);
    position: absolute;
    top: 2px; left: 2px;
    transition: transform 0.3s;
    width: calc(var(--toggle-height) - 4px);
  }

  label {
    margin-top: 0px;
  }

  &.active {
    .toggle-track { background-color: var(--lightbg-blue1); }
    .toggle-thumb { transform: translateX(calc(var(--toggle-width) - var(--toggle-height))); }
    .toggle-label { color: var(--lightbg-blue1); }
  }
}
</style> 
