<template>
</template>

<script setup>
  import {inject, onBeforeMount} from 'vue'
  import {utils} from '@/utils'

  onBeforeMount(function() { utils.setNavPosition('top') })
</script>

<style>
</style>
