<template>
  <div id='notes'>
    <LayoutSidePanel>
      <!-- Search -->
      <template #panel>
        <NotesSearch @select='selected=$event'/>
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
                <div><a class='h1' :href='`obsidian://open?vault=${selected.vault}&file=${selected.path}`'>Edit Note</a></div>
                <div><a class='h1' :href='`obsidian://new?vault=${selected.vault}&file=My New Note.md`'>Create New Note</a></div>
              </div>
            </div>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {inject, onBeforeMount, ref, watchEffect} from 'vue'
  import {api, utils} from '@/utils'
  import Markdown from '@/components/Markdown.vue'
  import NotesSearch from '@/views/notes/NotesSearch.vue'
  import NotesToc from '@/views/notes/NotesToc.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'
  import LayoutPaper from '@/components/LayoutPaper.vue'

  var cancelctrl = null           // Cancel controller
  const {user} = inject('user')   // Current User
  const loading = ref(false)      // True to show loading indicator
  const selected = ref(null)      // Currently selected note path
  const note = ref(null)          // Current note markdown contents
  const headings = ref(null)      // Current note headings

  onBeforeMount(function() { utils.setNavPosition('top') })

  // Watch Note
  // update the note contents when note 
  watchEffect(async function() {
    if (!selected.value) { return }
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {group:selected.value.group, path:selected.value.path}
      var {data} = await api.Obsidian.getNote(params, cancelctrl.signal)
      note.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }

  })
</script>

