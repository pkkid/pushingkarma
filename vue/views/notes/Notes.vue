<template>
  <div id='notes'>
    <SidePanel>
      <template #panel>
        <NotesSearch />
      </template>
      <template #content>
        bar
      </template>
    </SidePanel>
  </div>
</template>

<script setup>
  import {inject, onBeforeMount} from 'vue'
  import {utils} from '@/utils'
  import NotesSearch from '@/views/notes/NotesSearch.vue'
  import SidePanel from '@/components/SidePanel.vue'

  onBeforeMount(function() { utils.setNavPosition('top') })
</script>

