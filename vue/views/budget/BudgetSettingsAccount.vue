<template>
  <SortableItem class='budgetsettingsaccount' :itemid='account.id'>
    <Expandable ref='expandy' maxheight='250px' :itemid='account.id' @opened='emit("opened", $event)'>
      <template #header>
        <input type='text' v-model='accountName' spellcheck='false' autocomplete='off'
          @click.stop @keydown.ctrl.s.prevent='saveAccount' @keydown.enter.prevent='saveAccount'/>
      </template>
      <template #content>
        <div style='padding:5px 0px 15px 0px'>
          <!-- Help Tooltip -->
          <Tooltip width='400px' position='leftbottom' style='float:right; margin-right:5px;'>
            <template #tooltip>
              Configuration for importing bank transactions.
              <ul>
                <li><strong>file_pattern:</strong> Regex pattern to match the file name.</li>
                <li><strong>fid:</strong> Financial Institution ID (when importing qfx files).</li>
                <li><strong>columns:</strong> Dict of {dbcol: trxcol} pairs to map transactions in
                  the database. Database columns are: {trxid, date, payee, amount}.</li>
              </ul>
            </template>
            <i class='mdi mdi-information-outline'/>
          </Tooltip>
          <!-- Valid or Invalid JSON -->
          <Tooltip position='leftbottom' :text='jsonText' style='float:right; margin-right:5px;'>
            <i class='mdi' :class='jsonIcon'/>
          </Tooltip>
          <label>Import Configuration</label>
          <CodeEditor v-model='accountRules' :showLineNums='true' language='json' padding='8px' @save='saveAccount'/>
          <div class='button-row' style='margin-top:5px;'>
            <button @click='saveAccount'>Save Account</button>
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
</template>

<script setup>
  import {ref, watchEffect} from 'vue'
  import {CodeEditor, Expandable, SortableItem, Tooltip} from '@/components'
  import JSON5 from 'json5'

  const props = defineProps({
    account: {required:true},                                   // Account to be displayed
  })
  const emit = defineEmits(['opened'])                          // Emit opened event
  const expandy = ref(null)                                     // Reference to Expandable component
  const jsonIcon = ref('mdi-check')                             // Icon for JSON validation
  const jsonText = ref('Valid JSON')                            // Text for JSON validation
  const accountName = ref(props.account.name)                   // Name of the account
  const accountRules = ref(props.account.import_rules || '{}')  // Import rules for the account

  // Watch Account Rules
  // Validate the JSON text
  watchEffect(function() {
    try {
      JSON5.parse(accountRules.value)
      jsonIcon.value = 'mdi-check'
      jsonText.value = 'Valid JSON'
    } catch (e) {
      jsonIcon.value = 'mdi-alert-outline'
      jsonText.value = 'Invalid JSON'
    }
  })

  // Save Account
  // Save the account configuration
  const saveAccount = async function() {
    var rules = JSON5.parse(accountRules.value)
    console.log('TODO Save account', accountName.value, rules)
  }

  // Delete Account
  // Delete the specified account
  const deleteAccount = async function(event, accountid) {
    if (event.shiftKey) {
      console.log('TODO Delete acocunt', accountid)
    }
  }

  // Define Exposed
  defineExpose({
    account: props.account,
    open: function() { expandy.value.open() },
    close: function() { expandy.value.close() },
  })
</script>

<style>
  .budgetsettingsaccount {
    .codeeditor {
      height: 150px;
      width: 100%;
      font-size: 12px;
    }
  }
</style>

