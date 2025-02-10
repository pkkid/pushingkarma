<template>
  <div id='notes'>
    <SidePanel>
      <template #panel>
        <NotesSearch @select='selected=$event'/>
      </template>
      <template #content>
        {{selected}}
      </template>
    </SidePanel>
  </div>
</template>

<script setup>
  import {onBeforeMount, ref, watchEffect} from 'vue'
  import {api, utils} from '@/utils'
  import NotesSearch from '@/views/notes/NotesSearch.vue'
  import SidePanel from '@/components/SidePanel.vue'

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

