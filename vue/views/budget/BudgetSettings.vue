<template>
  <Modal id='budgetsettings' :visible='visible' closeButton closeOnEsc @close='emit("close")'>
    <template #header>
      <article><h2 style='margin:0px;'>Budget Settings</h2></article>
    </template>
    <article>
      <template v-if='accounts && categories'>
        <!-- Accounts -->
        <div class='accounts'>
          <h3 style='margin-top:0px;'>
            Accounts
            <div class='add-item' @click.stop='addAccount' style='float:right;'>Add New Account</div>
          </h3>
          <Sortable group='accounts' @sort='onSortAccounts'>
            <BudgetSettingsAccount v-for='account in accounts.items' :key='account.id' ref='accountPanels'
              :account='account' @opened='onAccountOpened' @updated='updateAccounts' @deleted='updateAccounts'/>
          </Sortable>
        </div>
        <!-- Categories -->
        <div class='categories'>
          <h3>
            Categories
            <div class='add-item' @click.stop='addCategory' style='float:right;'>Add New Category</div>
          </h3>
          <Sortable group='categories' @sort='onSortCategories' style='min-height:100px; max-height:300px; overflow-y:auto;'>
            <BudgetSettingsCategory v-for='category in categories.items' :key='category.id'
              :category='category' @updated='updateCategories'  @deleted='updateCategories'/>
          </Sortable>
        </div>
      </template>
      <!-- Loading -->
      <IconMessage v-else icon='pk' iconsize='40px' animation='gelatine' text='Loading data' ellipsis/>
    </article>
  </Modal>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {BudgetSettingsAccount, BudgetSettingsCategory} from '.'
  import {IconMessage, Modal, Sortable} from '@/components'
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
    var newaccount = {id:null, name:'New Account', rules:{}}
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
      border-radius: 0px;
      border-width: 0px;
      box-shadow: none;
      font-family: inherit;
      font-size: inherit;
      line-height: 30px;
      padding: 1px 6px 0px 6px;
      width: 250px;
      margin-left: 0px;
      transition: background-color 0.3s ease;
      &:focus {
        background-color:#8884;
        color: #000;
      }
    }

    /* Add Account or Category */
    h3 {
      margin-bottom: 5px;
      .add-item {
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 12px;
        opacity: 0;
        position: relative;
        top: 6px;
        &:hover { opacity:1 !important; }
      }
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
    .delete-category {
      opacity: 0;
      margin-right: 0px;
      position: relative;
      top: 5px;
    }
    .sortableitem:hover .delete-category { opacity:0.7; }
  }
</style>
