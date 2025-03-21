<template>
  <td :data-title='title' :data-name='name'>
    <div class='tdwrap' :class='name'>
      <slot></slot>
    </div>
  </td>
</template>

<script setup>
  import {computed} from 'vue'
  import {utils} from '@/utils'

  const props = defineProps({
    title: {type:String, required:true},    // Required column title
    name: {type:String},                    // Column name, defaults to camelCase title
  })

  const name = computed(function() {
    if (props.name) { return props.name }
    var camel = utils.title(props.title.toLowerCase()).replace(/ /g, '')
    return camel.charAt(0).toLowerCase() + camel.slice(1)
  })
</script>
