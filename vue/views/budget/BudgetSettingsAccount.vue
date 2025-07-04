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
          <Tooltip width='450px' position='leftbottom' style='float:right; margin-right:5px;'>
            <template #tooltip>
              Configuration for importing bank transactions. All fields are optional.
              Database columns are: {trxid, date, payee, amount, balance}.
              <pre><code>{{utils.dedent(`
                {
                  "file_pattern": "Fnmatch file name pattern to match",
                  "date_format": "Date format used in the imported file.",
                  "transactions": "XPath to transactions in qfx file.",
                  "balance": "XPath to account balance in qfx file.",
                  "balance_updated": "XPath to account balance date in qfx file.",
                  "inverse_amounts": "Set true to inverse amounts from imported file.",
                  "hidden": "Set true to hide this account in the UI.",
                  "columns": "{dbcol: trxcol} pairs to map transactions.",
                }`)}}</code></pre>
            </template>
            <i class='mdi mdi-information-outline'/>
          </Tooltip>
          <!-- Valid or Invalid JSON -->
          <Tooltip position='leftbottom' :text='jsonText' style='float:right; margin-right:5px;'>
            <i class='mdi' :class='jsonIcon'/>
          </Tooltip>
          <label>Import Configuration</label>
          <CodeEditor v-model='accountRules' :showlinenums='true' language='json' height='150px' @save='saveAccount'/>
          <div class='button-row' style='margin-top:5px;'>
            <button @click='saveAccount'>Save Account</button>
            <Tooltip position='left'>
              <template #tooltip>Delete Account<div class='subtext'>shift + double-click</div></template>
              <i class='mdi mdi-trash-can-outline delete-account' style='margin-left:auto;'
                @dblclick='deleteAccount($event)'/>
            </Tooltip>
          </div>
        </div>
      </template>
    </Expandable>
  </SortableItem>
</template>

<script setup>
  import {inject, ref, watchEffect} from 'vue'
  import {CodeEditor, Expandable, SortableItem, Tooltip} from '@/components'
  import {api, utils} from '@/utils'

  const props = defineProps({
    account: {required:true},                                   // Account to be displayed
  })
  const emit = defineEmits(['opened', 'updated', 'deleted'])    // Emit opened event
  const {notify} = inject('notify')                             // Notification callback
  const expandy = ref(null)                                     // Reference to Expandable component
  const jsonIcon = ref('mdi-check')                             // Icon for JSON validation
  const jsonText = ref('Valid JSON')                            // Text for JSON validation
  const accountName = ref(props.account.name)                   // Name of the account
  const accountRules = ref(utils.stringify(                     // Rules for the account
    props.account.rules || {}, {indent:2, maxlen:0}))

  // Watch Account Rules
  // Validate the JSON text
  watchEffect(function() {
    try {
      JSON.parse(accountRules.value)
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
    var name = accountName.value
    var rules = JSON.parse(accountRules.value)
    var {data} = props.account.id
      ? await api.Budget.updateAccount(props.account.id, {name, rules})
      : await api.Budget.createAccount({name, rules})
    emit('updated', data)
    // Create notification
    var action = props.account.id ? 'updated' : 'created'
    var title = `${data.name} Account ${utils.title(action)}`
    var message = `Successfully ${action} the account ${data.name}.`
    notify(title, message, 'mdi-check', 5000)
  }

  // Delete Account
  // Delete the specified account
  const deleteAccount = async function(event) {
    if (event.shiftKey) {
      if (props.account.id != null) {
        await api.Budget.deleteAccount(props.account.id)
      }
      emit('deleted', props.account.id)
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
      --padding: 8px;
      width: 100%;
      font-size: 10px;
      .codewrap { background-color:#efefed !important; }
    }
    .tooltip pre {
      background-color: #0002;
      border-radius: 4px;
      line-height: 12px;
      padding: 5px;
      code { padding: 0px; }
    }
  }
</style>

