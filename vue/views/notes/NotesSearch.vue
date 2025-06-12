<template>
  <div id='notessearch'>
    <!-- Search Input -->
    <div class='searchwrap'>
      <input ref='searchinput' class='searchinput' v-model='search' type='text' maxlength='100'
        spellcheck='false' autocomplete='off' @keydown.enter='updateNotes'
        @keydown.down='focusNext' @keydown.up='focusPrev'/>
      <i class='mdi mdi-magnify'/>
      <transition name='fade'>
        <i v-if='search.length' class='mdi mdi-close' @click='search=""' />
      </transition>
    </div>
    <!-- Search Results -->
    <div v-if='notes?.length > 0' ref='resultsdiv' class='results'>
      <a href='#' class='result' v-for='note in notes' :key='note.title' :class='{selected:note.path==selected?.path}'
        @click.prevent @click='$emit("select", note)' @keydown.enter='$emit("select", note)' 
        @keydown.down='focusNext' @keydown.up='focusPrev'>
        <i v-if='note.icon' class='icon mdi' :class='note.icon'/>
        {{note.title}}
        <i v-if='note.bucket=="private"' class='mdi mdi-lock' style='margin-left:5px'/>
        <!-- <div class='subtext'>{{utils.formatDate(note.mtime, 'MMM DD, YYYY')}}</div> -->
      </a>
    </div>
    <!-- Loading -->
    <div v-else>
      <div v-for='i in 3' :key='i' style='padding:20px 20px 0px 20px;'>
        <div class='empty-row'/>
        <div class='empty-row small short'/>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {onBeforeMount, onBeforeUnmount, ref} from 'vue'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  const emit = defineEmits([
    'results',      // New result set is loaded
    'select'        // User selects a new note
  ])
  const props = defineProps({
    selected: {},   // Currently selected note
  })

  var cancelctrl = null                   // Cancel controller
  const loading = ref(false)              // True to show loading indicator
  const notes = ref(null)                 // Current search results
  const search = ref('')                  // Current search string
  const resultsdiv = ref(null)            // Reference to resultsdiv elem
  const searchinput = ref(null)           // Reference to searchinput elem
  
  // On Before Mount
  // Fetch initial notes to display
  onBeforeMount(() => {
    updateNotes()
    hotkeys('f1', 'notes', function() {  searchinput.value.focus() })
    hotkeys.setScope('notes')
  })

  // On Before Mount
  // Unbind all note hotkeys
  onBeforeUnmount(() => {
    hotkeys.deleteScope('notes')
  })

  // Update Notes
  // when search.value changes
  const updateNotes = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var searchstr = search.value.length < 3 ? '' : search.value
      var {data} = await api.Obsidian.listNotes({search:searchstr}, cancelctrl.signal)
      notes.value = data.items
      emit('results', data.items)
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }

  // Focus Next
  // Focus on the next result
  const focusNext = function(event) {
    event.preventDefault()
    var current = document.activeElement
    if (current.classList.contains('result')) {
      var next = current.nextElementSibling
      if (next) { next.focus() }
    } else {
      var first = resultsdiv.value.querySelector('.result')
      if (first) { first.focus() }
    }
  }

  // Focus Prev
  // Focus on the previous result
  const focusPrev = function(event) {
    event.preventDefault()
    var current = document.activeElement
    if (current.classList.contains('result')) {
      var prev = current.previousElementSibling
      if (prev) { prev.focus() }
    }
  }
</script>

<style>
  #notessearch {
    width: var(--sidepanel-width);
    .results {
      height: calc(100vh - 102px);
      opacity: 0.7;
      overflow-y: scroll;
      transition: opacity 0.5s ease;
      &:hover, &:has(:focus) { opacity: 1; }
    }
    a.result {
      border-bottom: 0px solid #0000;
      border-left: 3px solid transparent;
      color: var(--darkbg-fg3);
      cursor: pointer;
      display: block;
      font-size: 12px;
      font-family: var(--fontfamily-article);
      overflow: hidden;
      padding: 7px 15px;
      text-overflow: ellipsis;
      transition: all 0.3s ease;
      user-select: none;
      white-space: nowrap;
      &:hover, &:focus, &.selected {
        color: var(--fgcolor);
        border-left: 3px solid var(--accent);
        background-color: #fff1;
      }
      .icon {
        font-size: 1.3em;
        color: var(--darkbg-fg1);
        margin-right: 5px;
        position: relative;
        top: 2px;
      }
    }
  }
</style>
