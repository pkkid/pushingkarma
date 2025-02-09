<template>
  <div id='notessearch'>
    <div class='inputwrap'>
      <input v-model='search' type='text' />
      <span class='icon search'>search</span>
      <transition name='fade'>
        <span v-if='search.length' class='icon clear-search close' @click='search=""'>close</span>
      </transition>
    </div>
  </div>
</template>

<script setup>
  import {ref} from 'vue'

  const search = ref('')
</script>

<style>
  #notessearch {
    inputwrap { position: relative; }
    input, input:focus {
      background-color: #0003;
      border-radius: 0px;
      border-width: 0px;
      box-shadow: none;
      color: var(--accent);
      line-height: 40px;
      outline: none;
      padding: 0px 30px 0px 38px;
      width: 100%;
    }
    .icon.search {
      position: absolute;
      font-size: 18px;
      top: 11px;
      left: 10px;
    }
    .icon.close {
      position: absolute;
      top: 8px;
      right: 5px;
      transition: opacity 0.3s ease;
    }
  }
</style>