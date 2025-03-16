<template>
  <div id='stockssearch'>
    <!-- Search Input -->
    <div class='searchwrap'>
      <input ref='searchinput' class='searchinput' v-model='search' type='text' maxlength='100'
        @keydown.enter='updateNotes' @keydown.down='focusNext' @keydown.up='focusPrev'/>
      <span class='icon search'>search</span>
      <transition name='fade'>
        <span v-if='search.length' class='icon clear-search close' @click='search=""'>close</span>
      </transition>
    </div>
    <!-- Pre-Canned Searches -->
    <div ref='resultsdiv' class='results'>
      <!-- <a href='#' class='result' v-for='note in notes' :key='note.title' :class='{selected:note.path==selected?.path}'
        @click.prevent @click='$emit("select", note)' @keydown.enter='$emit("select", note)' 
        @keydown.down='focusNext' @keydown.up='focusPrev'>
        {{note.title}}
        <div class='subtext'>{{utils.formatDate(note.mtime * 1000, 'MMM DD, YYYY')}}</div>
      </a> -->
    </div>
  </div>
</template>

<script setup>
  import {onBeforeMount, onBeforeUnmount, ref} from 'vue'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  const emit = defineEmits([
    'search'        // New search string
  ])

  var cancelctrl = null                   // Cancel controller
  const loading = ref(false)              // True to show loading indicator
  const search = ref('')                  // Current search string
  const searchinput = ref(null)           // Reference to searchinput elem
  
  // On Before Mount
  // Fetch initial notes to display
  onBeforeMount(() => {
    hotkeys('f1', 'stocks', function() {  searchinput.value.focus() })
    hotkeys.setScope('stocks')
  })

  // On Before Mount
  // Unbind all note hotkeys
  onBeforeUnmount(() => {
    hotkeys.deleteScope('stocks')
  })
</script>
