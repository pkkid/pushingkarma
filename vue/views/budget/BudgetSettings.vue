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
          <SortableItem v-for='account in accounts.items' :key='account.id' :itemid='account.id'>
            <Expandable ref='accountExpandies' maxheight='250px' :itemid='account.id' @opened='onAccountOpened'>
              <template #header>
                <input type='text' :value='account.name' spellcheck='false' autocomplete='off' @click.stop/>
              </template>
              <template #content>
                <div style='padding:5px 0px 15px 0px'>
                  <Tooltip width='400px' position='leftbottom' style='float:right; margin-right:5px;'>
                    <template #tooltip>
                      Rules for importing transactions files.
                      <ul>
                        <li><strong>file_pattern:</strong> Regex pattern to match the file name.</li>
                        <li><strong>fid:</strong> Financial Institution ID (when importing qfx files).</li>
                        <li><strong>columns:</strong> Dict of {dbcol: trxcol} pairs to map transactions in
                          the database. Database columns are: {trxid, date, payee, amount}.</li>
                      </ul>
                    </template>
                    <i class='mdi mdi-information-outline'/>
                  </Tooltip>
                  <h4>Import Configuration</h4>
                  <CodeEditor :value='account.import_config' :showLineNums='true' language='json' padding='8px'
                    style='height:150px; width:100%; font-size:12px;'/>
                  <div class='button-row' style='margin-top:5px;'>
                    <button>Save Account</button>
                    <Tooltip position='left'>
                      <template #tooltip>Delete Account<div class='subtext'>shift + double-click</div></template>
                      <i class='mdi mdi-trash-can-outline delete-account' style='margin-left:auto;'
                        @dblclick='deleteAccount($event, account.id)'/>
                    </Tooltip>
                  </div>
                </div>
              </template>
            </Expandable>
          </SortableItem>
        </Sortable>
      </div>
      <!-- Categories -->
      <div v-if='categories' class='categories'>
        <h3>Categories</h3>
        <Sortable group='categories' @sort='onSortCategories' style='min-height:100px; max-height:300px; overflow-y:auto;'>
          <SortableItem v-for='category in categories.items' :key='category.id' :itemid='category.id'>
            <input type='text' :value='category.name' spellcheck='false' autocomplete='off' @click.stop/>
            <Tooltip position='left' style='float:right;'>
              <template #tooltip>Delete Category<div class='subtext'>shift + double-click</div></template>
              <i class='mdi mdi-trash-can-outline delete-category' @dblclick='deleteCategory($event, category.id)'/>
            </Tooltip>
          </SortableItem>
        </Sortable>
      </div>
    </article>
  </Modal>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {CodeEditor, Expandable, Modal, Tooltip} from '@/components'
  import {Sortable, SortableItem} from '@/components/Sortable'
  import {api} from '@/utils'
  
  const emit = defineEmits(['close'])         // Emit close event
  const accounts = ref(null)                  // Accounts response from server
  const accountExpandies = ref([])            // Reference to account expandable components
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
    for (var i=0; i < accountExpandies.value.length; i++) {
      var expandy = accountExpandies.value[i]
      if (expandy.itemid == event.itemid) { continue }
      expandy.close()
    }
  }

  // Delete Account
  // Delete the specified account
  const deleteAccount = async function(event, accountid) {
    if (event.shiftKey) {
      console.log('Delete acocunt', accountid)
    }
  }

  // On Sort Categories
  // Update the categories sort order
  const onSortCategories = async function(event) {
    var {data} = await api.Budget.sortCategories({sortlist:event.sortlist})
    categories.value = data
  }

  // Delete Category
  // Delete the specified account
  const deleteCategory = async function(event, accountid) {
    if (event.shiftKey) {
      console.log('Delete cateogry', accountid)
    }
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
