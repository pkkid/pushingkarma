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
            <Expandable maxheight='250px'>
              <template #header>{{account.name}}</template>
              <template #content>
                <div style='padding:5px 0px 15px 0px'>
                  <h4>Import Configuration</h4>
                  <CodeEditor :value='account.import_config' language='json' padding='8px'
                    style='height:150px; width:100%; font-size:12px;'/>
                  <div class='button-row' style='margin-top:5px;'>
                    <button>Save Account</button>
                    <button>Delete Account</button>
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
            {{category.name}}
          </SortableItem>
        </Sortable>
      </div>
    </article>
  </Modal>
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {Sortable, SortableItem} from '@/components/Sortable'
  import {api} from '@/utils'
  import CodeEditor from '@/components/CodeEditor.vue'
  import Expandable from '@/components/Expandable.vue'
  import Modal from '@/components/Modal.vue'
  
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

  // On Sort Accounts
  // Update the accounts sort order
  const onSortAccounts = function(event) {
    console.log('onSortAccounts', event)
  }

  // On Sort Categories
  // Update the categories sort order
  const onSortCategories = function(event) {
    console.log('onSortCategories', event)
  }
</script>

<style>
  #budgetsettings .modal-wrap {
    width: 600px;
    padding-bottom: 10px;
  }
</style>
