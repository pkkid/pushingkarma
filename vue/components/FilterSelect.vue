<template>
  <div class='filterselect'>
    <input v-model='_value' spellcheck='false' autocomplete='off' @keydown='onKeyDown'/>
    <div v-if='fchoices' class='fsdropdown lightbg'>
      <div v-for='(choice, i) in fchoices' :key='choice.id' :ref='el => choicerefs[i]=el' class='fschoice' 
        :class='{focused:focused?.name == choice.name}'>
        {{choice.name}}
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed, nextTick, ref, watch} from 'vue'

  const props = defineProps({
    choices: {required:true},               // List of [{id, name}] for all choices
    value: {required:true},                 // Initial value for the input
  })
  const _value = ref(props.value || '')     // Current input value
  const choicerefs = ref([])                // Track choice DOM elements
  const focused = ref(null)                 // Track focused choice
  const emit = defineEmits(['keydown'])     // Emit keydown event to parent

  // Filtered Choices
  // Filter the choices based on the input value
  const fchoices = computed(function() {
    const query = _value.value?.toLowerCase() || ''
    const sorted = props.choices.slice().sort((a, b) => a.name.localeCompare(b.name))
    if (!query) { return sorted }
    var startswith=[], contains=[]
    for (const choice of sorted) {
      if (choice.name.toLowerCase().startsWith(query)) { startswith.push(choice) }
      else if (choice.name.toLowerCase().includes(query)) { contains.push(choice) }
    }
    var filtered = [...startswith, ...contains]
    if (filtered.length == 1 && filtered[0].name.toLowerCase() === query) { return null }
    return filtered
  })

  // Watch Filtered Choices
  // Update the focused choice to the first in the list
  watch(fchoices, function() {
    if (!fchoices.value) { return null }
    focused.value = fchoices.value[0]
  }, {immediate:true})

  // Watch Focused Choice
  // Make sure the focused choice is in view
  watch(focused, async function(newval) {
    await nextTick()
    if (!fchoices.value || !newval) { return }
    var i = fchoices.value.findIndex(c => c.name == newval.name)
    if (i != -1 && choicerefs.value[i]) {
      choicerefs.value[i].scrollIntoView({block:'nearest'})
    }
  })

  // On Keydown
  // Handle input key events
  const onKeyDown = function(event) {
    // Propagate keydown event to parent not using it here
    var keys = ['ArrowUp', 'ArrowDown', 'Enter']
    if (!fchoices.value || !keys.includes(event.key)) { return emit('keydown', event) }
    // Handle key events
    if (event.key == 'ArrowUp' && focused.value) {
      event.preventDefault()
      const index = fchoices.value.findIndex(choice => choice.name === focused.value.name)
      if (index > 0) { focused.value = fchoices.value[index - 1] }
    } else if (event.key === 'ArrowDown' && focused.value) {
      event.preventDefault()
      const index = fchoices.value.findIndex(choice => choice.name === focused.value.name)
      if (index < fchoices.value.length - 1) { focused.value = fchoices.value[index + 1] }
    } else if (event.key === 'Enter' && focused.value) {
      event.preventDefault()
      _value.value = focused.value.name
      emit('keydown', event)
    }
  }
</script>

<style>
  .filterselect {
    position: relative;
    overflow: visible;
    .fsdropdown {
      border-color: #bbb;
      border-radius: 0px 0px 6px 6px;
      border-style: solid;
      border-width: 0px 1px 1px 1px;
      box-shadow: 0px 2px 4px #0004, 0px 4px 10px #0002;
      left: 0px;
      line-height: 1.5;
      max-height: 200px;
      overflow-y: auto;
      overscroll-behavior: contain;
      padding: 2px 0px 5px 0px;
      position: absolute;
      top: 100%;
      width: 100%;
      .fschoice {
        cursor: default;
        padding: 0px 8px;
        &.focused, &:hover {
          background-color: var(--lightbg-bg2);
        }
      }
    }
  }
</style>
