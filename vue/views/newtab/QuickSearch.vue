<template>
  <Teleport to='body'>
    <Transition name='quicksearch-fade'>
      <!-- v-show (not v-if) keeps the search input on the page while hidden. Adding and removing it
           confused Bitwarden when filling the login form opened from this panel. -->
      <div v-show='visible' class='quicksearch-overlay' @mousedown.self='close'>
        <div class='quicksearch'>
          <div class='quicksearch-input'>
            <i class='mdi mdi-magnify'/>
            <!-- data-bwignore and autocomplete=off keep password managers from treating this search box as
                 a login field, which confused Bitwarden when filling the login form opened from this panel -->
            <input ref='inputEl' v-model='query' type='text' placeholder='Search bookmarks' spellcheck='false'
              autocomplete='off' data-bwignore='true' data-1p-ignore data-lpignore='true'
              @input='resetSelection' @keydown='onKeydown'/>
          </div>
          <!-- Bookmarks and actions (log in when logged out, log out when logged in) -->
          <div v-if='results.length || query.trim()' ref='resultsEl' class='quicksearch-results'>
            <a v-for='(result, i) in results' :key='result.key' :href='result.item?.url || "#"' class='result'
              :class='{selected:i === selected}' @mousemove='selected = i' @click='onClick($event, result)'>
              <div class='title'><i v-if='result.icon' class='mdi' :class='result.icon'/>{{result.title}}</div>
              <div class='subtitle'>{{result.subtitle}}</div>
            </a>
            <div v-if='!results.length' class='empty'>No bookmarks found</div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
  <Account :visible='showLogin' @close='showLogin = false'/>
</template>

<script setup>
  import {computed, inject, nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue'
  import {api} from '@/utils'
  import {Account} from '@/views/site'
  import {askDelete, confirming, load, openUrl, search, tree} from './bookmarks'

  const visible = ref(false)                        // True when the panel is displayed
  const query = ref('')                             // Search input text
  const selected = ref(0)                           // Highlighted result index
  const inputEl = ref(null)                         // Search input element
  const resultsEl = ref(null)                       // Results list element
  const showLogin = ref(false)                      // True when the login modal is displayed
  const {user, setUser} = inject('user')            // Current user, bookmarks require login
  const {globalvars} = inject('globalvars')         // Global vars, apikey_auth is true when signed in by api key

  // Actions
  // Log in when logged out, log out when logged in. Keywords are what you can
  // type to find the action alongside bookmark results.
  const actions = computed(function() {
    if (!user.value) {
      return [{key:'login', title:'Log in', subtitle:'Log in to see your bookmarks', icon:'mdi-login',
        keywords:'log in login sign in', run:() => login()}]
    }
    if (globalvars.value?.apikey_auth) { return [] }  // Logging out does nothing when signed in by api key
    const name = `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.email
    return [{key:'logout', title:'Log out', subtitle:`Logged in as ${name}`, icon:'mdi-logout',
      keywords:'log out logout sign out', run:() => logout()}]
  })

  // Results
  // Logged out or empty search shows the actions. Otherwise bookmarks matching the
  // search, after any actions whose keywords match.
  const results = computed(function() {
    const words = query.value.toLowerCase().split(/\s+/).filter(Boolean)
    if (!user.value || !words.length) { return actions.value }
    const bookmarks = search(query.value, 50).map(r => ({key:r.item.id, title:r.item.title || r.item.url, subtitle:r.subtitle, item:r.item}))
    const matching = actions.value.filter(a => words.every(word => a.keywords.includes(word)))
    return [...matching, ...bookmarks]
  })

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
  watch(results, function() { selected.value = Math.min(selected.value, results.value.length - 1) })
  watch(confirming, async function(value) {
    if (value || !visible.value) { return }
    await nextTick()
    inputEl.value?.focus()
  })

  // Watch User
  // Close the login modal once logged in so the bookmarks bar is visible
  watch(user, function(value) { if (value) { showLogin.value = false } })

  // Open / Close
  // Show the panel with an empty search, loading bookmarks if the bar hasn't yet
  const open = async function() {
    query.value = ''
    resetSelection()
    visible.value = true
    await nextTick()
    inputEl.value?.focus()
    if (user.value && !tree.value.length) { load() }
  }
  const close = () => visible.value = false

  // Reset Selection
  // Highlight the first result, except for an empty search while logged in, where
  // nothing is highlighted so a stray enter can't log you out
  const resetSelection = function() {
    selected.value = user.value && !query.value.trim() ? -1 : 0
  }

  // Login / Logout
  // Login shows the same login modal used on the main site. Logout also clears
  // the bookmarks from memory.
  const login = function() {
    close()
    showLogin.value = true
  }
  const logout = async function() {
    close()
    await api.Main.logout()
    setUser(null)
    tree.value = []
  }

  // Run
  // Run an action, or open a bookmark (ctrl+enter or ctrl+click in a new tab)
  const run = function(result, event) {
    if (result.run) { return result.run() }
    openUrl(result.item.url, event)
    close()
  }

  // On Click
  // Actions run here, bookmark links open themselves so middle-click still works
  const onClick = function(event, result) {
    if (result.run) {
      event.preventDefault()
      result.run()
    } else {
      close()
    }
  }

  // On Document Keydown
  // F1 toggles the panel, escape closes it. Ignored while the delete
  // confirmation or login modal is open so escape only closes that.
  const onDocumentKeydown = function(event) {
    if (confirming.value || showLogin.value) { return }
    if (event.key === 'F1') {
      event.preventDefault()
      visible.value ? close() : open()
    } else if (event.key === 'Escape' && visible.value) {
      close()
    }
  }

  // On Keydown
  // Arrow keys select a result, enter opens or runs it (ctrl+enter opens bookmarks
  // in a new tab), and delete asks to delete a bookmark. Delete only applies with the cursor at the end of
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
      event.preventDefault()  // Stop this enter from also submitting the login form once it has focus
      run(results.value[selected.value], event)
    } else if (event.key === 'Delete' && atEnd && results.value[selected.value]?.item) {
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
      .title .mdi { font-size: 16px; margin-right: 8px; vertical-align: -2px; }
      .subtitle { color: var(--darkbg-fg4); font-size: 12px; margin-top: 2px; }
      &.selected { background-color: #fff1; }
      &.selected .title { color: var(--darkbg-fg0); }
    }
    .empty { color: var(--darkbg-fg4); font-size: 13px; font-style: italic; padding: 12px 14px; }
  }
  .quicksearch-fade-enter-active, .quicksearch-fade-leave-active { transition: opacity 0.15s ease; }
  .quicksearch-fade-enter-from, .quicksearch-fade-leave-to { opacity: 0; }
</style>
