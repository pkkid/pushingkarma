<template>
  <div id='budgetsearch'>
    <div class='searchinputwrap'>
      <input type='text' v-model='_search' placeholder='Search Transactions' class='searchinput' @keydown.enter='search=_search || null'>
      <transition name='fade'><i v-if='_search?.length' class='mdi mdi-close' @click='search=""; _search=""'/></transition>
    </div>
    <div class='searchfilterswrap'>
      <template v-for='filter in suggested_filters' :key='filter.name'>
        <a v-if='!filter.selected' @click='search=filter.query'>{{filter.name}}</a>
        <span v-else class='selected'>{{filter.name}}</span>
      </template>
    </div>
  </div>
</template>

<script setup>
  import {ref, watch} from 'vue'
  import {useUrlParams} from '@/composables'

  const props = defineProps({
    suggested_filters: {type:Array},            // Enables demo mode
  })
  const emit = defineEmits(['update:search'])   // Emit search change
  const {search} = useUrlParams({search:{}})    // Method & path url params
  const _search = ref(search.value)             // Temp search before enter

  // Watch Search
  // Update transactions and _search.value
  watch(search, function() {
    _search.value = search.value
    emit('update:search', search.value)
  })
</script>

<style>
  /* Search Wrap */
  #budgetsearch {
    text-align: right;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    margin-top: -10px;
    align-items: center;
    padding-top: 22px;
    float: right;
    width: 50%;

    .searchinputwrap {
      display: flex;
      flex-direction: column;
      width: 100%;
      position: relative;
      input {
        width: 100%;
        border-radius: 20px;
        padding: 5px 15px;
      }
      .mdi-close {
        position: absolute;
        right: 10px;
        top: 9px;
        font-size: 14px;
      }
    }

    .searchfilterswrap {
      text-align: right;
      margin-right: 20px;
      font-size: 13px;
      margin-top: 3px;
      width: 100%;
      color: var(--lightbg-fg3);
      * { margin:0px 4px; padding:2px 0px; }
      .selected {
        background-color: var(--lightbg-bg2);
        border-radius: 4px;
        padding: 2px 5px;
      }
    }
  }
</style>
