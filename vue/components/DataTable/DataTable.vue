<template>
  <div class='datatable' ref='datatable'>
    <table v-if='items !== null'>
      <!-- Header Row (dynamically created) -->
      <thead><tr>
        <th v-for='head in headers' :key='head.name' :data-name='head.name'>
          <div class='thwrap' :class='head.name'>{{head.title}}</div>
        </th>
      </tr></thead>
      <tbody>
        <!-- Body Rows -->
        <tr v-for='(item, rownum) in items' :key='item[keyattr]'>
          <slot name='columns' :item="item" :rownum="rownum"></slot>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
  import {ref, nextTick, onMounted, watch} from 'vue'

  const datatable = ref(null)
  const headers = ref(null)
  const props = defineProps({
    items: {type:Array, required:true},
    keyattr: {type:String, required:true},
  })

  // Watch Items
  // Update the headers from the data attributes of the first row
  onMounted(function() { updateHeaders() })
  watch(() => props.items, function() { updateHeaders() })

  const updateHeaders = async function() {
    if (props.items?.length == 0) { return }
    await nextTick()
    var tds = datatable.value.querySelectorAll('tbody tr:first-child td')
    headers.value = Array.from(tds).map(td => ({
      title: td.dataset.title,
      name: td.dataset.name,
    }))
  }
</script>

<style>
  .datatable {
    background-color: var(--lightbg-bg0);
    border: 1px solid var(--lightbg-bg3);
    border-radius: 6px;
    padding: 1px;
    table {
      border-collapse: collapse;
      border-spacing: 0;
      width: 100%;
    }
    th, td { padding: 1px 6px; }
    th { background-color: var(--lightbg-bg2); }
    td { border-top: 1px solid var(--lightbg-bg3); } 
    .thwrap {
      font-family: var(--fontfamily-title);
      font-size: 12px;
      font-weight: bold;
      color: var(--lightbg-fg2);
      text-align: left;
    }
    .tdwrap {
      font-size: 13px;
      color: var(--lightbg-fg2);
    }
  }
</style>
