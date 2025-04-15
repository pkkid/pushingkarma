<template>
  <Modal id='budgetsettings' :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <template #header>
      <article><h2 style='margin:0px;'>Budget Settings</h2></article>
    </template>
    <article>
      <!-- Accounts -->
      <div v-if='accounts' class='accounts'>
        <h3 style='margin-top:0px;'>
          <Tooltip text='Add Account' position='left' style='float:right; margin-top:3px;'>
            <i class='mdi mdi-plus add-item' @click.stop='addAccount'/>
          </Tooltip>
          Accounts
        </h3>
        <Sortable group='accounts' @sort='onSortAccounts'>
          <BudgetSettingsAccount v-for='account in accounts.items' :key='account.id' ref='accountPanels'
            :account='account' @opened='onAccountOpened' @updated='updateAccounts' @deleted='updateAccounts'/>
        </Sortable>
      </div>
      <!-- Categories -->
      <div v-if='categories' class='categories'>
        <h3>
          <Tooltip text='Add Category' position='left' style='float:right; margin-top:3px;'>
            <i class='mdi mdi-plus add-item' @click.stop='addCategory'/>
          </Tooltip>
          Categories
        </h3>
        <Sortable group='categories' @sort='onSortCategories' style='min-height:100px; max-height:300px; overflow-y:auto; overscroll-behavior:contain;'>
          <BudgetSettingsCategory v-for='category in categories.items' :key='category.id'
            :category='category' @updated='updateCategories'  @deleted='updateCategories'/>
        </Sortable>
      </div>
    </article>
  </Modal>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {BudgetSettingsAccount, BudgetSettingsCategory} from '.'
  import {Modal, Sortable, Tooltip} from '@/components'
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
    var {data} = await api.Budget.listAccounts()
    accounts.value = data
  }

  // Update Categories
  // Update the categories list
  const updateCategories = async function() {
    var {data} = await api.Budget.listCategories()
    categories.value = data
  }

  // Add Account
  // Create a new account object
  const addAccount = async function() {
    if (accounts.value.items[0].name == 'New Account') { return }
    var newaccount = {id:null, name:'New Account', import_rules:{}}
    accounts.value.items.unshift(newaccount)
  }

  // Add Category
  // Create a new category object
  const addCategory = async function() {
    if (categories.value.items[0].name == 'New Category') { return }
    var newcategory = {id:null, name:'New Category'}
    categories.value.items.unshift(newcategory)
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

    /* Add Account or Category */
    h3 .add-item {
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 18px;
      opacity: 0;
      &:hover { opacity:1 !important; }
    }
    h3:hover .add-item { opacity:0.6; }

    /* Delete Account or Category */
    .delete-account,
    .delete-category {
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 1.2em;
      margin-right: 5px;
      opacity:0.6;
      &:hover { opacity:1 !important; color:var(--lightbg-red0) !important; }
    }
    .delete-account:hover,
    .delete-category:hover { color: var(--lightbg-red0) !important; }
    .delete-category { opacity:0; margin-right:0px; position:relative; top:1px; }
    .sortableitem:hover .delete-category { opacity:0.7; }
  }
</style>
