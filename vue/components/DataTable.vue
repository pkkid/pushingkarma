<template>
  <table class='datatable' v-if='items !== null'>
    <thead><tr><slot name='headers'></slot></tr></thead>
    <tbody ref='tbody'>
      <tr v-for='item in items' :key='item[keyattr]'>
        <slot name='columns' :item="item"></slot>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
  import {ref, onMounted, watchEffect, nextTick} from 'vue'

  const headers = ref([])
  const tbody = ref(null)
  const props = defineProps({
    items: {type:Array, required:true},
    keyattr: {type:String, required:true},
  })

  watchEffect(async function() {
    await nextTick()
    const firstRow = tbody.value?.querySelector('tr')
    console.log('firstRow', firstRow)
  })
</script>
