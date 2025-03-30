<template>
  <SortableItem :itemid='category.id'>
    <input type='text' :value='categoryName' spellcheck='false' autocomplete='off'
      @click.stop @keydown.ctrl.s.prevent='saveCategory' @keydown.enter.prevent='saveCategory'/>
    <Tooltip position='left' style='float:right;'>
      <template #tooltip>Delete Category<div class='subtext'>shift + double-click</div></template>
      <i class='mdi mdi-trash-can-outline delete-category' @dblclick='deleteCategory($event, category.id)'/>
    </Tooltip>
  </SortableItem>
</template>

<script setup>
  import {ref} from 'vue'
  import {SortableItem, Tooltip} from '@/components'

  const props = defineProps({
    category: {required:true},                    // Account to be displayed
  })
  const categoryName = ref(props.category.name)   // Name of the account

  // Save Cateogry
  // Save the category configuration
  const saveCategory = async function() {
    console.log('TODO Save category', categoryName.value)
  }

  // Delete Category
  // Delete the specified account
  const deleteCategory = async function(event, accountid) {
    if (event.shiftKey) {
      console.log('TODO Delete cateogry', accountid)
    }
  }

</script>
