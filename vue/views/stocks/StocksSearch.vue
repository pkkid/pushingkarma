<template>
  <div id='stockssearch'>
    <!-- Search Input -->
    <div class='searchwrap'>
      <input ref='searchinput' class='searchinput' v-model='_search' type='text' maxlength='100'
        spellcheck='false' autocomplete='off' @keydown.enter='updateSearch(_search)'/>
      <span class='icon search'>search</span>
      <transition name='fade'>
        <span v-if='search?.length' class='icon clear-search close' @click='updateSearch("")'>close</span>
      </transition>
    </div>
    <!-- Pre-Canned Searches -->
    <div class='menu'>
      <div class='item'>
        <span class='icon'>payments</span>
        Stock Groups
      </div>
      <div v-for='(gsrch, name) in stockgroups' :key='name' class='subitem link'
        :class='{selected:search == gsrch}' @click='updateSearch(gsrch)'>
        <div class='name'>{{name}}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {inject, onBeforeMount, onBeforeUnmount, ref, watchEffect} from 'vue'
  import hotkeys from 'hotkeys-js'

  const props = defineProps({
    stockgroups: {type:Object, required:true},
  })
  const {search, updateSearch} = inject('search')
  const _search = ref(search.value)       // Local search string
  const searchinput = ref(null)           // Reference to searchinput elem
  const emit = defineEmits(['search'])    // New search string
  
  // Watch Search
  // Update local search string
  watchEffect(() => _search.value = search.value)

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
