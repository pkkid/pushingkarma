<template>
  <div class='datatable' ref='datatable'>
    <div class='datatable-wrap'>
      <table v-if='items !== null'>
        <!-- Header (dynamically created) -->
        <thead><tr>
          <th v-for='head in headers' :key='head.name' :class='head.name'>
            <div class='thwrap'>{{head.title}}
              <div v-if='head.subtext' class='subtext'>{{head.subtext}}</div>
            </div>
          </th>
        </tr></thead>
        <!-- Body -->
        <tbody>
          <tr v-for='(item, row) in items' :key='item[keyattr]'>
            <slot name='columns' :item='item' :row='row'></slot>
          </tr>
        </tbody>
        <!-- Footer -->
        <tfoot v-if='footer'>
          <tr><slot name='footer' :item='footer'></slot></tr>
        </tfoot>
      </table>
    </div>
    <div v-if='nextpage' ref='scrollwatch'>
      <slot name='scrollwatch'></slot>
    </div>
  </div>
</template>

<script setup>
  import {ref, nextTick, onBeforeUnmount, onMounted, watch} from 'vue'

  var observer = null                         // Observer for infinite scroll
  var lastemitlen = 0                         // Length of items when last emitted
  const datatable = ref(null)                 // Reference to datatable element
  const headers = ref(null)                   // Headers for the table
  const scrollwatch = ref(null)               // Reference to scrollwatch element
  const props = defineProps({
    items: {type:Array, required:true},       // Array of items to display
    footer: {type:Object, default:null},      // Footer item object
    keyattr: {type:String, required:true},    // Attribute to use as key
    infinite: {type:Boolean, default:false},  // Enable infinite scroll
    nextpage: {type:String, default:null},    // Next page URL for infinite scroll
  })
  const emit = defineEmits(['getNextPage'])

  // Watch Items
  // Update the headers from the data attributes of the first row
  watch(() => props.items, function() {
    updateHeaders()
    lastemitlen = 0
  })

  // On Mounted
  // Update headers and initalize infinity scroll observer
  onMounted(function() {
    updateHeaders()
    if (props.infinite) { initObserver() }
  })

  // On Before Unmount
  // Disconnect the observer
  onBeforeUnmount(() => {
    if (observer) { observer.disconnect() }
  })
  
  // Init Observer
  // Create an observer to detect when the last row is visible
  const initObserver = async function() {
    if (observer) { observer.disconnect() }
    observer = new IntersectionObserver(function(entries) {
      if (entries[0].isIntersecting && props.items.length !== lastemitlen && props.nextpage) {
        lastemitlen = props.items.length
        console.log('Sending getNextPage')
        emit('getNextPage', props.nextpage)
      }
    }, {root:null, rootMargin:'200px', threshold:0})
    await nextTick()
    if (scrollwatch.value) {
      observer.observe(scrollwatch.value)
    }
  }

  // Update Headers
  // Read header names from the first row of the table
  const updateHeaders = async function() {
    if (props.items?.length == 0) { return }
    await nextTick()
    var tds = datatable.value.querySelectorAll('tbody tr:first-child td')
    headers.value = Array.from(tds).map(td => ({
      name: td.dataset.name,
      title: td.dataset.title,
      subtext: td.dataset.subtext,
    }))
  }
</script>

<style>
  .datatable-wrap {
    background-color: var(--lightbg-bg0);
    border-radius: 6px;
    border: 1px solid var(--lightbg-bg3);
    padding: 1px;

    table {
      border-collapse: collapse;
      border-spacing: 0;
      max-width: 100%;
    }
    /* th, td { padding: 1px 6px; } */
    thead th {
      background-color: var(--lightbg-bg2);
      &:first-child { border-top-left-radius: 4px; }
      &:last-child { border-top-right-radius: 4px; }
    }
    td { border-top: 1px solid var(--lightbg-bg3); } 
    .thwrap {
      padding: 1px 6px;
      font-family: var(--fontfamily-title);
      font-size: 12px;
      font-weight: bold;
      color: var(--lightbg-fg2);
      text-align: inherit;
      width: 100%;
    }
    .tdwrap {
      font-size: 13px;
      color: var(--lightbg-fg2);
      text-align: inherit;
      width: 100%;
    }
    tfoot td {
      background-color: var(--lightbg-bg2);
      &:first-child { border-bottom-left-radius: 4px; }
      &:last-child { border-bottom-right-radius: 4px; }
    }
  }
</style>
