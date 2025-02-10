<template>
  <div id='notessearch'>
    
    <!-- Search Input -->
    <div class='inputwrap'>
      <input v-model='search' type='text' maxlength='100'/>
      <span class='icon search'>search</span>
      <transition name='fade'>
        <span v-if='search.length' class='icon clear-search close' @click='search=""'>close</span>
      </transition>
    </div>

    <!-- Search Results -->
    <div class='results'>
      <div class='result' v-for='note in notes' :key='note.title' @click='$emit("newSelection", note.title)'>
        {{note.title}}
        <div class='subtext'>{{utils.formatDate(note.mtime * 1000, 'MMM DD, YYYY')}}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {onBeforeMount, ref, watch} from 'vue'
  import {api, utils} from '@/utils'

  var cancelctrl = null           // Cancel controller
  const loading = ref(false)      // True to show loading indicator
  const notes = ref(null)         // Current search results
  const search = ref('')          // Current search string
  
  onBeforeMount(() => { updateNotes() })
  watch(search, utils.debounce(function() { updateNotes() }))

  // Update Notes
  // when search.value changes
  const updateNotes = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var searchstr = search.value.length < 3 ? '' : search.value
      var {data} = await api.Obsidian.search({search:searchstr}, cancelctrl.signal)
      notes.value = data.results
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }
</script>

<style>
  #notessearch {
    inputwrap { position: relative; }
    input, input:focus {
      background-color: #0003;
      border-radius: 0px;
      border-width: 0px;
      box-shadow: none;
      color: var(--accent);
      line-height: 40px;
      outline: none;
      padding: 0px 30px 0px 38px;
      width: 100%;
    }
    .icon.search {
      position: absolute;
      font-size: 18px;
      top: 11px;
      left: 10px;
    }
    .icon.close {
      position: absolute;
      top: 8px;
      right: 5px;
      transition: opacity 0.3s ease;
    }

    .results {
      height: calc(100vh - 102px);
      opacity: 0.7;
      overflow-y: scroll;
      transition: opacity 0.5s ease;
      &:hover { opacity: 1; }
    }
    .result {
      border-left: 3px solid transparent;
      cursor: pointer;
      font-size: 12px;
      overflow: hidden;
      padding: 13px 15px 13px 12px;
      text-overflow: ellipsis;
      user-select: none;
      white-space: nowrap;
      &.highlighted,
      &:hover {
        border-left: 3px solid var(--accent);
        background-color: #fff1;
      }
      .subtext {
        font-size: 10px;
        font-weight: 400;
        color: var(--dim);
        padding-top: 2px;
      }
    }
  }
</style>