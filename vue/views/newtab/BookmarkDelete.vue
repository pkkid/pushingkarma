<template>
  <ConfirmModal id='bookmark-confirm' :visible='Boolean(confirming)' theme='dark' confirmLabel='Delete' danger
    :title='confirming?.title' :message='confirming?.message' @confirm='confirmDelete' @cancel='cancel'/>
</template>

<script setup>
  // Bookmark Delete
  // Delete confirmation shared by the bookmarks bar and the F1 quick search.
  // Open it with askDelete(item) from bookmarks.js.
  import {inject} from 'vue'
  import {ConfirmModal} from '@/components'
  import {api} from '@/utils'
  import {confirming, load, tree} from './bookmarks'

  const {notify} = inject('notify')
  const cancel = () => confirming.value = null

  // Confirm Delete
  // Delete the bookmark once confirmed. On failure notify and reload.
  const confirmDelete = async function() {
    const {item} = confirming.value
    confirming.value = null
    try {
      const {data} = await api.Bookmarks.deleteBookmark(item.id)
      tree.value = data
    } catch (err) {
      notify('Bookmarks Error', err.response?.data?.message || err.message, 'mdi-alert')
      load()
    }
  }
</script>
