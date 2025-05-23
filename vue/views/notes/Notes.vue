<template>
  <div id='notes'>
    <LayoutSidePanel>
      <!-- Search -->
      <template #panel>
        <NotesSearch :selected='selected' @select='selected=$event' @results='onResults'/>
      </template>
      <template #content>
        <LayoutPaper>
          <!-- Note Content-->
          <template #content>
            <template v-if='note'>
              <h1>{{note.title}}
                <div class='subtext'>{{utils.formatDate(note.mtime * 1000, 'MMM DD, YYYY')}}</div>
              </h1>
              <Markdown :source='note.content' @headings='headings=$event'/>
            </template>
            <!-- Loading Content -->
            <IconMessage v-else icon='pk' iconsize='40px' animation='gelatine' text='Loading note' ellipsis/>
          </template>
          <!-- Table of Contents & Controls-->
          <template #controls>
            <div v-if='note'>
              <NotesToc :title='note.title' :headings='headings' />
              <div v-if='user?.id'>
                <h2>Obsidian Options</h2>
                <div class='submenu'>
                  <div><a class='h1' :href='`obsidian://open?vault=${note.vault}&file=${note.path}`'>Edit Note</a></div>
                  <div><a class='h1' :href='`obsidian://new?vault=${note.vault}&file=My New Note.md`'>Create New Note</a></div>
                </div>
              </div>
            </div>
            <!-- Loading TOC -->
            <div v-else>
              <div v-for='i in 3' :key='i'>
                <div class='empty-row big' style='margin-top:40px;'/>
                <div class='empty-row short'/>
                <div class='empty-row short'/>
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
  import {NotesSearch, NotesToc} from '@/views/notes'
  import {IconMessage, LayoutPaper, LayoutSidePanel, Markdown} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'

  var cancelctrl = null           // Cancel controller
  const {user} = inject('user')   // Current User
  const loading = ref(false)      // True to show loading indicator
  const selected = ref(null)      // Currently selected note path
  const note = ref(null)          // Current note markdown contents
  const headings = ref(null)      // Current note headings
  const {bucket, path} = useUrlParams({bucket:{}, path:{}})

  onBeforeMount(function() { utils.setNavPosition('top') })

  // Watch Selected
  // update group & path when selection changes
  watchEffect(async function() {
    if (!selected.value) { return }
    bucket.value = selected.value.bucket
    path.value = selected.value.path
  })

  // Watch Group & Path
  // update note when these change
  watchEffect(async function() {
    if ((!bucket.value) || (!path.value)) { return }
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var {data} = await api.Obsidian.getNote(bucket.value,
        path.value, null, cancelctrl.signal)
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
    if (!bucket.value && !path.value) {
      bucket.value = results[0].bucket
      path.value = results[0].path
    }
  }
</script>

<style>
  #notes {
    article:has(#bannerimage) h1 { margin-top: 170px; }
  }
</style>
