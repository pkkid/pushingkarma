<template>
  <div id='stocks'>
    <LayoutPaper id='budgetsettings' width='1000px'>
      <template #content>
        <h1>Stocks</h1>
      </template>
    </LayoutPaper>
  </div>
</template>

<script setup>
  import {onBeforeMount} from 'vue'
  import {utils} from '@/utils'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import LayoutPaper from '@/components/LayoutPaper.vue'

  onBeforeMount(function() { utils.setNavPosition('top') })
</script>

<style>
  #stocks {
    
  }
</style>