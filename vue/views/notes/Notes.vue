<template>
  <div id='notes'>
    <LayoutSidePanel>
      <!-- Search -->
      <template #panel>
        <NotesSearch :selected='selected' @select='selected=$event' @results='onResults'/>
      </template>
      <template #content>
        <LayoutPaper v-if='note'>
            <!-- Note Content-->
            <template #content>
            <h1>{{note.title}}
              <div class='subtext'>{{utils.formatDate(note.mtime * 1000, 'MMM DD, YYYY')}}</div>
            </h1>
            <Markdown :source='note.content' @headings='headings=$event'/>
          </template>
          <!-- Table of Contents & Controls-->
          <template #controls>
            <NotesToc :title='note.title' :headings='headings' />
            <div v-if='user?.id'>
              <h2>Obsidian Options</h2>
              <div class='submenu'>
                <div><a class='h1' :href='`obsidian://open?vault=${note.vault}&file=${note.path}`'>Edit Note</a></div>
                <div><a class='h1' :href='`obsidian://new?vault=${note.vault}&file=My New Note.md`'>Create New Note</a></div>
              </div>
            </div>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {inject, nextTick, onBeforeMount, ref, watchEffect} from 'vue'
  import {LayoutPaper, LayoutSidePanel} from '@/components/Layout'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import {api, utils} from '@/utils'
  import Markdown from '@/components/Markdown.vue'
  import NotesSearch from '@/views/notes/NotesSearch.vue'
  import NotesToc from '@/views/notes/NotesToc.vue'

  var cancelctrl = null           // Cancel controller
  const {user} = inject('user')   // Current User
  const loading = ref(false)      // True to show loading indicator
  const selected = ref(null)      // Currently selected note path
  const note = ref(null)          // Current note markdown contents
  const headings = ref(null)      // Current note headings
  const {group, path} = useUrlParams({
    group: {type: String},
    path: {type: String}
  })

  onBeforeMount(function() { utils.setNavPosition('top') })

  // Watch Selected
  // update group & path when selection changes
  watchEffect(async function() {
    if (!selected.value) { return }
    group.value = selected.value.group
    path.value = selected.value.path
  })

  // Watch Group & Path
  // update note when these change
  watchEffect(async function() {
    if ((!group.value) || (!path.value)) { return }
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {group:group.value, path:path.value}
      var {data} = await api.Obsidian.getNote(params, cancelctrl.signal)
      note.value = data
      window.scrollTo(0, 0)
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  })

  // On Results Loaded
  // If no note selected, load the first note
  const onResults = function(results) {
    if (!selected.value && results?.length >= 1) { selected.value = results[0] }
  }
</script>

