<template>
  <div id='notes'>
    <LayoutSidePanel>
      <!-- Search -->
      <template #panel>
        Hello Side Panel!
      </template>
      <template #content>
        <LayoutPaper width='1200'>
          <template #content>
            Hello Content!
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {inject, onBeforeMount} from 'vue'
  import {utils} from '@/utils'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'

  onBeforeMount(function() { utils.setNavPosition('top') })
</script>