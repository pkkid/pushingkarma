<template>
  <SortableItem :itemid='category.id'>
    <input type='text' v-model='categoryName' spellcheck='false' autocomplete='off'
      @click.stop @keydown.ctrl.s.prevent='saveCategory' @keydown.enter.prevent='saveCategory'/>
    <Tooltip position='left' style='float:right;'>
      <template #tooltip>Delete Category<div class='subtext'>shift + double-click</div></template>
      <i class='mdi mdi-trash-can-outline delete-category' @dblclick='deleteCategory($event)'/>
    </Tooltip>
  </SortableItem>
</template>

<script setup>
  import {inject, ref} from 'vue'
  import {SortableItem, Tooltip} from '@/components'
  import {api, utils} from '@/utils'

  const props = defineProps({
    category: {required:true},                        // Category to be displayed
  })
  const emit = defineEmits(['updated', 'deleted'])    // Emit opened event
  const {notify} = inject('notify')                             // Notification callback
  const categoryName = ref(props.category.name)       // Name of the category

  // Save Cateogry
  // Save the category configuration
  const saveCategory = async function() {
    var name = categoryName.value
    var {data} = props.category.id
      ? await api.Budget.updateCategory(props.category.id, {name})
      : await api.Budget.createCategory({name})
    emit('updated', data)
    // Create notification
    var action = props.category.id ? 'updated' : 'created'
    var title = `${data.name} Category ${utils.title(action)}`
    var message = `Successfully ${action} the account ${data.name}.`
    notify(title, message, 'mdi-check', 5000)
  }

  // Delete Category
  // Delete the specified category
  const deleteCategory = async function(event) {
    if (event.shiftKey) {
      await api.Budget.deleteCategory(props.category.id)
      emit('deleted', props.category.id)
    }
  }
</script>
