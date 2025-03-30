<template>
  <Modal id='budgetsettings' :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <template #header>
      <article><h2 style='margin:0px;'>Budget Settings</h2></article>
    </template>
    <article>
      <!-- Accounts -->
      <div v-if='accounts' class='accounts'>
        <h3 style='margin-top:0px;'>Accounts</h3>
        <Sortable group='accounts' @sort='onSortAccounts'>
          <BudgetSettingsAccount v-for='account in accounts.items' :key='account.id'
            ref='accountPanels' :account='account' @opened='onAccountOpened'/>
        </Sortable>
      </div>
      <!-- Categories -->
      <div v-if='categories' class='categories'>
        <h3>Categories</h3>
        <Sortable group='categories' @sort='onSortCategories' style='min-height:100px; max-height:300px; overflow-y:auto;'>
          <BudgetSettingsCategory v-for='category in categories.items' :key='category.id' :category='category'/>
        </Sortable>
      </div>
    </article>
  </Modal>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {BudgetSettingsAccount, BudgetSettingsCategory} from '.'
  import {Modal, Sortable} from '@/components'
  import {api} from '@/utils'
  
  const emit = defineEmits(['close'])         // Emit close event
  const accounts = ref(null)                  // Accounts response from server
  const accountPanels = ref([])               // Reference to BudgetSettingsAccount components
  const categories = ref(null)                // Categories response from server
  const props = defineProps({
    visible: {type:Boolean, required:true},   // True when modal is visible
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

  // On Sort Accounts
  // Update the accounts sort order
  const onSortAccounts = async function(event) {
    var {data} = await api.Budget.sortAccounts({sortlist:event.sortlist})
    accounts.value = data
  }

  // On Account Opened
  // Close all the other account expandies
  const onAccountOpened = function(event) {
    for (var panel of accountPanels.value) {
      if (panel.account.id == event.itemid) { continue }
      panel.close()
    }
  }

  // On Sort Categories
  // Update the categories sort order
  const onSortCategories = async function(event) {
    var {data} = await api.Budget.sortCategories({sortlist:event.sortlist})
    categories.value = data
  }
</script>

<style>
  #budgetsettings .modal-wrap {
    width: 600px;
    padding-bottom: 10px;

    .sortable input[type=text] {
      background-color: transparent;
      /* border-radius: 0px; */
      border-width: 0px;
      box-shadow: none;
      font-family: inherit;
      font-size: inherit;
      line-height: 22px;
      padding: 1px 6px 0px 6px;
      width: 200px;
      margin-left: -6px;
      transition: background-color 0.3s ease;
      &:focus { background-color:#0001; }
    }
    .delete-account,
    .delete-category {
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 1.2em;
      margin-right: 5px;
      opacity:0.6;
      &:hover {
        color: var(--lightbg-red0) !important;
        opacity: 1 !important;
      }
    }
    .delete-category { opacity:0; margin-right:0px; position:relative; top:1px; }
    .sortableitem:hover .delete-category { opacity:0.7; }
  }
</style>
