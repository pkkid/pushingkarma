<template>
  <div class='selectinput'>
    <input v-model='_value' spellcheck='false' autocomplete='off' @keydown='onKeyDown'/>
    <div v-if='fchoices' class='selectinput-dropdown lightbg'>
      <div v-for='(choice, i) in fchoices' :key='choice.id' :ref='el => choicerefs[i]=el' class='selectinput-choice' 
        :class='{focused:focused?.name == choice.name}'>
        {{choice.name}}
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed, nextTick, ref, watch} from 'vue'

  const props = defineProps({
    choices: {required:true},                 // List of [{id, name}] for all choices
    modelValue: {required:true},              // Initial value for the input
  })
  const _value = ref(props.modelValue || '')  // Current input value
  const choicerefs = ref([])                  // Track choice DOM elements
  const focused = ref(null)                   // Track focused choice
  const emit = defineEmits([
    'update:modelValue',                      // Emit updated value to parent  
    'keydown'                                 // Emit keydown event to parent
  ])     

  // Watch Value
  // Update local _value or pass new modelValue to parent
  watch(() => props.modelValue, function(newval) {
    if (newval != _value.value) { _value.value = newval }
  })
  watch(_value, function(newval) {
    emit('update:modelValue', newval)
  })

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
    if (filtered.length == 0) { return sorted }  // maybe this is weird?
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
    var keys = ['ArrowUp', 'ArrowDown', 'Enter']
    if (!fchoices.value || !keys.includes(event.key)) { return emit('keydown', event) }
    if (event.key == 'ArrowUp' && focused.value) { onArrowUp(event) }
    else if (event.key === 'ArrowDown' && focused.value) { onArrowDown(event) }
    else if (event.key === 'Enter' && focused.value && fchoices.value) { onEnter(event) }
  }

  // On Arrow Up
  // Handle arrow up key event
  const onArrowUp = function(event) {
    event.preventDefault()
    const index = fchoices.value.findIndex(choice => choice.name === focused.value.name)
    if (index > 0) { focused.value = fchoices.value[index - 1] }
  }

  // On Arrow Down
  // Handle arrow down key event
  const onArrowDown = function(event) {
    event.preventDefault()
    const index = fchoices.value.findIndex(choice => choice.name === focused.value.name)
    if (index < fchoices.value.length - 1) { focused.value = fchoices.value[index + 1] }
  }

  // On Enter
  // Handle enter key event
  const onEnter = async function(event) {
    event.preventDefault()
    _value.value = focused.value.name
    await nextTick()
    emit('keydown', event)
  }
</script>

<style>
  .selectinput {
    position: relative;
    overflow: visible;
    .selectinput-dropdown {
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
      .selectinput-choice {
        cursor: default;
        padding: 0px 8px;
        &.focused, &:hover {
          background-color: var(--lightbg-bg2);
        }
      }
    }
  }
</style>
