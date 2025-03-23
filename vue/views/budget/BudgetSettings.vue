<template>
  <Modal :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <article id='budgetsettings' class='lightbg'>
      <h2 style='margin-top:0px;'>Budget Settings</h2>
      <div v-if='accounts' class='accounts'>
        <h3>Accounts</h3>
        <Sortable>
          <SortableItem v-for='account in accounts.results' :key='account.id'>
            <div class='name'>{{account.name}}</div>
          </SortableItem>
        </Sortable>
      </div>
      <div v-if='categories' class='categories'>
        <h3>Categories</h3>
      </div>
    </article>
  </Modal>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {api, utils} from '@/utils'
  import Modal from '@/components/Modal.vue'
  import {Sortable, SortableItem} from '@/components/Sortable'

  const emit = defineEmits(['close'])
  const accounts = ref(null)
  const categories = ref(null)
  const props = defineProps({
    visible: {type:Boolean, required:true},
  })

  // Watch Visisble
  // Update accounts and categories when modal becomes visible
  watchEffect(function() {
    if (props.visible == true) {
      updateAccounts()
      updateCategories()
    }
  })

  // Update Accounts
  // Update the accounts list
  const updateAccounts = async function() {
    var {data} = await api.Budget.getAccounts()
    accounts.value = data
  }

  // Update Categories
  // Update the categories list
  const updateCategories = async function() {
    var {data} = await api.Budget.getCategories()
    categories.value = data
  }

</script>

<style>
  #budgetsettings {
    padding: 20px;
    width: 600px;
  }
</style>
