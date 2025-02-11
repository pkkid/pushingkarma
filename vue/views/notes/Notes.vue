<template>
  <div id='notes'>
    <LayoutSidePanel>
      <template #panel>
        <NotesSearch @select='selected=$event'/>
      </template>
      <template #content>
        <div class='contentwrap'>
          <LayoutPaper>
            <template #content>
              <h1>{{note.title}}</h1>
              <Markdown v-if='note' :source='note.content' />
            </template>
            <template #controls>
              Controls
            </template>
          </LayoutPaper>
        </div>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {onBeforeMount, ref, watchEffect} from 'vue'
  import {api, utils} from '@/utils'
  import Markdown from '@/components/Markdown.vue'
  import NotesSearch from '@/views/notes/NotesSearch.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'
  import LayoutPaper from '@/components/LayoutPaper.vue'

  var cancelctrl = null           // Cancel controller
  const loading = ref(false)      // True to show loading indicator
  const selected = ref(null)      // Currently selected note path
  const note = ref(null)          // Current note markdown contents

  onBeforeMount(function() { utils.setNavPosition('top') })

  // Watch Note
  // update the note contents when note 
  watchEffect(async function() {
    if (!selected.value) { return }
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var {data} = await api.Obsidian.getNote({path:selected.value}, cancelctrl.signal)
      note.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }

  })
</script>

