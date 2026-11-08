<template>
  <div id='notessearch'>
    <!-- Search Input -->
    <div class='searchwrap'>
      <input ref='searchinput' class='searchinput' v-model='search' type='text' maxlength='100'
        spellcheck='false' autocomplete='off' @keydown.enter='updateNotes'
        @keydown.down='focusNext' @keydown.up='focusPrev'/>
      <i class='mdi mdi-magnify'/>
      <transition name='fade'>
        <i v-if='search.length' class='mdi mdi-close' @click='search=""; updateNotes()' />
      </transition>
    </div>
    <!-- Sort Options -->
    <div class='sortbar'>
      <span class='label' id='notessortlabel'>Sort by</span>
      <div class='sort' role='group' aria-labelledby='notessortlabel'>
        <button v-for='option in SORTS' :key='option.id' type='button'
          :class='{on:sortby == option.id}' @click='sortby = option.id'>{{option.label}}</button>
      </div>
    </div>
    <!-- Search Results -->
    <div v-if='notes?.length > 0' ref='resultsdiv' class='results'>
      <template v-for='group in groups' :key='group.name'>
        <div v-if='group.name' class='groupheader' :style='{color:group.color}'>
          <i v-if='group.name == PRIVATE' class='mdi mdi-lock'/>{{group.name}}
        </div>
        <a href='#' class='result' v-for='note in group.notes' :key='`${note.bucket}/${note.path}`'
          :class='{selected:note.path==selected?.path}'
          @click.prevent @click='$emit("select", note)' @keydown.enter='$emit("select", note)'
          @keydown.down='focusNext' @keydown.up='focusPrev'>
          <i v-if='note.icon' class='icon mdi' :class='note.icon'/>
          <span class='title'>{{note.title}}</span>
          <i v-if='note.bucket == "private" && !group.name' class='lock mdi mdi-lock'/>
          <span class='date'>{{utils.formatDate(note.mtime, 'MMM D, YYYY')}}</span>
        </a>
      </template>
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
  import {computed, onBeforeMount, onBeforeUnmount, ref} from 'vue'
  import {useStorage} from '@/composables'
  import {api, utils} from '@/utils'
  import hotkeys from 'hotkeys-js'

  const emit = defineEmits([
    'results',      // New result set is loaded
    'select'        // User selects a new note
  ])
  const props = defineProps({
    selected: {},   // Currently selected note
  })

  const OTHER = 'Other'                   // Group for notes at the top level of the vault
  const PRIVATE = 'Private'               // Single group for all private notes
  const GROUPCOLORS = {                   // Header color for each folder group
    'Family': 'var(--darkbg-blue1)',
    'Gaming': 'var(--darkbg-purple1)',
    'Operating Systems': 'var(--darkbg-aqua1)',
    'Programming': 'var(--darkbg-yellow1)',
    'Software': 'var(--darkbg-orange1)',
    'Synology': 'var(--darkbg-green1)',
    [OTHER]: 'var(--darkbg-fg2)',
    [PRIVATE]: 'var(--darkbg-red1)',
  }
  const SPARECOLORS = [                   // Colors for folders not listed above, used in turn
    'var(--darkbg-blue1)', 'var(--darkbg-purple1)', 'var(--darkbg-aqua1)',
    'var(--darkbg-yellow1)', 'var(--darkbg-orange1)', 'var(--darkbg-green1)',
  ]
  var cancelctrl = null                   // Cancel controller
  const loading = ref(false)              // True to show loading indicator
  const notes = ref(null)                 // Current search results
  const search = ref('')                  // Current search string
  const searched = ref('')                // Search string used for the current results
  const sortby = useStorage('notes.sortby', 'category')  // How to group and sort the notes
  const SORTS = [                         // Sort pill options
    {id:'category', label:'Category'},
    {id:'name', label:'Name'},
    {id:'date', label:'Date'},
  ]
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
      searched.value = searchstr
      notes.value = data.items
      emit('results', data.items)
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }

  // Groups
  // Search results stay in one list ordered by relevance. Otherwise the notes are
  // sorted by name, by date (newest first), or grouped by their top level folder
  // with top level notes under Other and all private notes in one Private group.
  // Each group gets a header color from GROUPCOLORS, or the next spare color.
  const groups = computed(function() {
    if (searched.value) { return [{name:null, notes:notes.value}] }
    if (sortby.value == 'name') { return [{name:null, notes:[...notes.value].sort((a, b) => a.title.localeCompare(b.title))}] }
    if (sortby.value == 'date') { return [{name:null, notes:[...notes.value].sort((a, b) => new Date(b.mtime) - new Date(a.mtime))}] }
    var grouped = {}
    for (var note of notes.value) {
      var name = note.bucket == 'private' ? PRIVATE : note.path.includes('/') ? note.path.split('/')[0] : OTHER
      grouped[name] = grouped[name] || []
      grouped[name].push(note)
    }
    var last = [OTHER, PRIVATE]
    var names = Object.keys(grouped).filter(name => !last.includes(name)).sort()
    names.push(...last.filter(name => grouped[name]))
    var spare = 0
    return names.map(function(name) {
      var color = GROUPCOLORS[name] || SPARECOLORS[spare++ % SPARECOLORS.length]
      return {name, color, notes:grouped[name]}
    })
  })

  // Focus Next
  // Focus on the next result, skipping over group headers
  const focusNext = function(event) {
    focusResult(event, 1)
  }

  // Focus Prev
  // Focus on the previous result, skipping over group headers
  const focusPrev = function(event) {
    focusResult(event, -1)
  }

  // Focus Result
  // Move focus by offset through the results. When no result has focus, moving
  // down focuses the first result and moving up does nothing.
  function focusResult(event, offset) {
    event.preventDefault()
    var results = [...resultsdiv.value.querySelectorAll('.result')]
    var index = results.indexOf(document.activeElement)
    var target = index < 0 ? (offset > 0 ? results[0] : null) : results[index + offset]
    if (target) { target.focus() }
  }
</script>

<style>
  #notessearch {
    width: var(--sidepanel-width);
    /* Sort pills, styled like the Popular/Recent toggle in the project list */
    .sortbar {
      align-items: center;
      display: flex;
      gap: 12px;
      height: 40px;
      padding: 0px 15px 0px 18px;
      .label {
        color: var(--darkbg-fg2);
        font-family: var(--fontfamily-article);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
      }
    }
    .sort {
      background-color: var(--darkbg-bgh);
      border-radius: 6px;
      display: flex;
      gap: 2px;
      padding: 2px;
      button {
        background: none;
        border: 0px;
        border-radius: 4px;
        color: var(--darkbg-fg3);
        cursor: pointer;
        font-family: var(--fontfamily-article);
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        &.on { background-color:#3c3836; color:var(--darkbg-fg0); }
      }
    }
    .results {
      height: calc(100vh - 142px);
      opacity: 0.7;
      overflow-y: scroll;
      transition: opacity 0.5s ease;
      &:hover, &:has(:focus) { opacity: 1; }
    }
    /* Folder name above each group of notes */
    .groupheader {
      color: var(--darkbg-fg4);
      font-family: var(--fontfamily-article);
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 2.5px;
      padding: 16px 18px 6px 18px;
      text-transform: uppercase;
      user-select: none;
      .mdi { margin-right: 5px; }
    }
    a.result {
      border-bottom: 0px solid #0000;
      border-left: 3px solid transparent;
      color: var(--darkbg-fg3);
      align-items: center;
      cursor: pointer;
      display: flex;
      font-size: 12px;
      font-family: var(--fontfamily-article);
      gap: 8px;
      padding: 7px 15px;
      transition: all 0.3s ease;
      user-select: none;
      white-space: nowrap;
      .title { flex: 1; min-width: 0px; overflow: hidden; text-overflow: ellipsis; }
      .lock { flex-shrink: 0; font-size: 12px; }
      .date { color:var(--darkbg-fg4); flex-shrink:0; font-family:var(--fontfamily-code); font-size:9.5px; }
      &:hover, &:focus, &.selected {
        color: var(--fgcolor);
        border-left: 3px solid var(--accent);
        background-color: #fff1;
      }
      .icon {
        color: var(--darkbg-fg1);
        flex-shrink: 0;
        font-size: 1.3em;
      }
    }
  }
</style>
