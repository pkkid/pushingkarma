<template>
  <Teleport to='body'>
    <Transition name='quicksearch-fade'>
      <div v-if='visible' class='quicksearch-overlay' @mousedown.self='close'>
        <div class='quicksearch'>
          <div class='quicksearch-input'>
            <i class='mdi mdi-magnify'/>
            <input ref='inputEl' v-model='query' type='text' placeholder='Search bookmarks' spellcheck='false'
              @input='selected = 0' @keydown='onKeydown'/>
          </div>
          <div v-if='query.trim()' ref='resultsEl' class='quicksearch-results'>
            <a v-for='(result, i) in results' :key='result.item.id' :href='result.item.url' class='result'
              :class='{selected:i === selected}' @mousemove='selected = i' @click='close'>
              <div class='title'>{{result.item.title || result.item.url}}</div>
              <div class='subtitle'>{{result.subtitle}}</div>
            </a>
            <div v-if='!results.length' class='empty'>No bookmarks found</div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import {computed, nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue'
  import {askDelete, confirming, load, openUrl, search, tree} from './bookmarks'

  const visible = ref(false)                        // True when the panel is displayed
  const query = ref('')                             // Search input text
  const selected = ref(0)                           // Highlighted result index
  const inputEl = ref(null)                         // Search input element
  const resultsEl = ref(null)                       // Results list element
  const results = computed(() => search(query.value, 50))

  // On Mounted / Before Unmount
  // Listen for F1 anywhere on the page
  onMounted(function() { document.addEventListener('keydown', onDocumentKeydown) })
  onBeforeUnmount(function() { document.removeEventListener('keydown', onDocumentKeydown) })

  // Watch Selected
  // Keep the highlighted result scrolled into view
  watch(selected, async function(index) {
    await nextTick()
    resultsEl.value?.children[index]?.scrollIntoView({block:'nearest'})
  })

  // Watch Results / Confirming
  // Keep the selection in range after a delete, and refocus the search input
  // once the delete confirmation closes
  watch(results, function() { selected.value = Math.max(0, Math.min(selected.value, results.value.length - 1)) })
  watch(confirming, async function(value) {
    if (value || !visible.value) { return }
    await nextTick()
    inputEl.value?.focus()
  })

  // Open / Close
  // Show the panel with an empty search, loading bookmarks if the bar hasn't yet
  const open = async function() {
    query.value = ''
    selected.value = 0
    visible.value = true
    await nextTick()
    inputEl.value?.focus()
    if (!tree.value.length) { load() }
  }
  const close = () => visible.value = false

  // On Document Keydown
  // F1 toggles the panel, escape closes it. Ignored while the delete
  // confirmation is open so escape only cancels the confirmation.
  const onDocumentKeydown = function(event) {
    if (confirming.value) { return }
    if (event.key === 'F1') {
      event.preventDefault()
      visible.value ? close() : open()
    } else if (event.key === 'Escape' && visible.value) {
      close()
    }
  }

  // On Keydown
  // Arrow keys select a result, enter opens it (ctrl+enter in a new tab), and
  // delete asks to delete it. Delete only applies with the cursor at the end of
  // the input so it can still delete text in the middle of the query.
  const onKeydown = function(event) {
    const input = event.target
    const atEnd = input.selectionStart === input.value.length && input.selectionEnd === input.value.length
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      selected.value = Math.min(selected.value + 1, results.value.length - 1)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      selected.value = Math.max(selected.value - 1, 0)
    } else if (event.key === 'Enter' && results.value[selected.value]) {
      openUrl(results.value[selected.value].item.url, event)
      close()
    } else if (event.key === 'Delete' && atEnd && results.value[selected.value]) {
      event.preventDefault()
      askDelete(results.value[selected.value].item)
    }
  }
</script>

<style>
  .quicksearch-overlay {
    backdrop-filter: blur(3px);
    background-color: #0004;
    display: flex;
    inset: 0px;
    justify-content: center;
    padding-top: 18vh;
    position: fixed;
    z-index: 90;
  }
  .quicksearch {
    align-self: flex-start;
    background-color: var(--darkbg-bg0);
    border: 1px solid #fff2;
    border-radius: 10px;
    box-shadow: 0px 20px 60px #000c;
    color: var(--darkbg-fg3);
    font-family: var(--fontfamily-article);
    overflow: hidden;
    width: min(640px, calc(100vw - 32px));
    .quicksearch-input {
      position: relative;
      .mdi {
        color: var(--darkbg-fg4);
        font-size: 22px;
        left: 18px;
        line-height: 1;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        &::before { line-height: 1; }
      }
      input, input:focus {
        background-color: transparent;
        border: none;
        box-shadow: none;
        color: var(--darkbg-fg1);
        font-family: var(--fontfamily-article);
        font-size: 20px;
        height: 56px;
        padding: 0px 20px 0px 52px;
        width: 100%;
        &::placeholder { color: var(--darkbg-fg4); }
      }
    }
    .quicksearch-results {
      border-top: 1px solid #fff1;
      max-height: 50vh;
      overflow-y: auto;
      padding: 6px;
    }
    .result, .result:visited {
      border-radius: 6px;
      color: inherit;
      display: block;
      padding: 8px 12px;
      text-decoration: none;
      .title, .subtitle { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .title { color: var(--darkbg-fg2); font-size: 14px; }
      .subtitle { color: var(--darkbg-fg4); font-size: 12px; margin-top: 2px; }
      &.selected { background-color: #fff1; }
      &.selected .title { color: var(--darkbg-fg0); }
    }
    .empty { color: var(--darkbg-fg4); font-size: 13px; font-style: italic; padding: 12px 14px; }
  }
  .quicksearch-fade-enter-active, .quicksearch-fade-leave-active { transition: opacity 0.15s ease; }
  .quicksearch-fade-enter-from, .quicksearch-fade-leave-to { opacity: 0; }
</style>
