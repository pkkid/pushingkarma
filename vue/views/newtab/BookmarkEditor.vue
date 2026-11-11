<template>
  <Modal id='bookmark-editor' :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <form class='bookmark-editor' @submit.prevent='save'>
      <h2>{{item ? `Edit ${item.kind === 'folder' ? 'Folder' : 'Bookmark'}` : 'Add to Bookmarks'}}</h2>
      <div v-if='!item' class='kinds'>
        <button v-for='kind in kinds' :key='kind.value' type='button' :class='{active:form.kind === kind.value}'
          @click='form.kind = kind.value'>{{kind.label}}</button>
      </div>
      <template v-if='form.kind !== "separator"'>
        <label for='bookmark-title'>{{form.kind === 'folder' ? 'Folder name' : 'Title'}}</label>
        <input id='bookmark-title' ref='titleEl' v-model='form.title' type='text' spellcheck='false'/>
      </template>
      <template v-if='form.kind === "link"'>
        <label for='bookmark-url'>URL</label>
        <input id='bookmark-url' v-model='form.url' type='text' spellcheck='false'/>
      </template>
      <label for='bookmark-parent'>Folder</label>
      <select id='bookmark-parent' v-model='form.parent'>
        <option :value='null'>Bookmarks Bar</option>
        <option v-for='folder in parentFolders' :key='folder.id' :value='folder.id'>{{folder.path}}</option>
      </select>
      <div v-if='error' class='error'>{{error}}</div>
      <div class='buttons'>
        <button type='submit'>Save</button>
        <button type='button' @click='emit("close")'>Cancel</button>
      </div>
    </form>
  </Modal>
</template>

<script setup>
  import {computed, nextTick, ref, watch} from 'vue'
  import {Modal} from '@/components'

  const emit = defineEmits(['close', 'save'])
  const titleEl = ref(null)                         // Title input, focused when opened
  const form = ref({})                              // Values being edited {kind, title, url, parent}
  const error = ref(null)                           // Validation error message
  const kinds = [{value:'link', label:'Bookmark'}, {value:'folder', label:'Folder'}, {value:'separator', label:'Separator'}]
  const props = defineProps({
    visible: {type:Boolean, required:true},         // Display the editor
    item: {type:Object, default:null},              // Bookmark to edit, null to add a new one
    parent: {type:Number, default:null},            // Current (or default) parent folder id
    folders: {type:Array, required:true},           // All folders [{id, path, ancestors}]
  })

  // Parent Folders
  // A folder can not be moved inside itself or any of its descendants
  const parentFolders = computed(function() {
    if (props.item?.kind !== 'folder') { return props.folders }
    return props.folders.filter(f => f.id !== props.item.id && !f.ancestors.includes(props.item.id))
  })

  // Watch Visible
  // Reset the form every time the editor is opened
  watch(() => props.visible, async function(visible) {
    if (!visible) { return }
    const item = props.item || {kind:'link', title:'', url:''}
    form.value = {kind:item.kind, title:item.title, url:item.url, parent:props.parent}
    error.value = null
    await nextTick()
    titleEl.value?.focus()
  })

  // Save
  // Validate the form and emit the cleaned up values
  const save = function() {
    const data = {...form.value, title:form.value.title.trim(), url:form.value.url.trim()}
    if (data.kind === 'link' && !data.url) { return error.value = 'URL is required.' }
    if (data.kind === 'folder' && !data.title) { return error.value = 'Folder name is required.' }
    if (data.kind === 'link' && !/^[a-z][a-z0-9+.-]*:/i.test(data.url)) { data.url = `https://${data.url}` }
    emit('save', data)
  }
</script>

<style>
  #bookmark-editor .modal-wrap { min-width: 420px; }
  .bookmark-editor {
    display: flex;
    flex-direction: column;
    h2 { margin-top: 0px; }
    .kinds {
      display: flex;
      gap: 4px;
      margin-bottom: 5px;
      button.active { background-color: var(--lightbg-blue1); color: #fff; }
    }
    .error { color: var(--lightbg-red0); font-size: 12px; margin-top: 10px; }
    .buttons { display: flex; gap: 8px; margin-top: 20px; }
  }
</style>
