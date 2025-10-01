<template>
  <div id='budget'>
    <LayoutSidePanel>
      <!-- Side Panel (Navigation) -->
      <template #panel>
        <div v-if='accounts' class='menu'>
          <!-- Transactions -->
          <a href='/budget' class='item link' @click.prevent="view=null"
            :class='{selected:view==null && !showSettings}'>
            <i class='mdi mdi-credit-card-outline'/>
            Transactions
          </a>
          <template v-for='account in accounts' :key='account.id'>
            <div v-if='!account.rules?.hidden' class='subitem account'>
              <div class='name'>{{account.name}} Balance</div>
              <div class='balance'>{{utils.usd(account.balance, places=0)}}</div>
              <div class='lastupdate'>Updated {{utils.formatDate(account.balance_updated, '')}}</div>
            </div>
          </template>
          <!-- Year Overview -->
          <a href='/budget?view=year' class='item link' @click.prevent="view='year'"
            :class='{selected:view=="year" && !showSettings}'>
            <i class='mdi mdi-checkbook'/>
            Year Overview
          </a>
          <div class='subitem account'>
            <div class='name'>Total Spent {{utils.formatDate(new Date(), 'YYYY')}}</div>
            <div class='balance'>{{utils.usd(sumAccounts('spent'), places=0)}}</div>
            <div class='lastupdate'>Average {{utils.usd(avgAccounts('spent'), places=0)}} / month</div>
          </div>
          <div class='subitem account'>
            <div class='name'>Total Saved {{utils.formatDate(new Date(), 'YYYY')}}</div>
            <div class='balance'>{{utils.usd(sumAccounts('saved'), places=0)}}</div>
            <div class='lastupdate'>Average {{utils.usd(avgAccounts('saved'), places=0)}} / month</div>
          </div>
          <!-- Settings -->
          <div class='item link' :class='{selected:showSettings}' @click='showSettings=true'>
            <i class='mdi mdi-cog'/>
            Settings
          </div>
        </div>
        <div v-else style='padding:0px 20px;'>
          <div v-for='i in 2' :key='i'>
            <div class='empty-row big' style='margin-top:40px;'/>
            <div class='empty-row short'/>
            <div class='empty-row small short'/>
          </div>
        </div>
      </template>
      <!-- Content -->
      <template #content>
        <Dropzone @filesDropped='upload' text='Drop Transactions' subtext='Hold shift for safe import'>
          <BudgetYear v-if="view=='year'" :demo='demo'/>
          <BudgetTransactions v-else :demo='demo'/>
        </Dropzone>
      </template>
    </LayoutSidePanel>
  </div>
  <BudgetSettings :visible='showSettings' @close='showSettings=false'/>
</template>

<script setup>
  import {inject, onBeforeMount, ref} from 'vue'
  import {BudgetSettings, BudgetTransactions, BudgetYear} from '@/views/budget'
  import {LayoutSidePanel} from '@/components/Layout'
  import {Dropzone} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'

  const {demo, view} = useUrlParams({demo:{type:Boolean}, view:{}})  // Current view
  const {notify} = inject('notify')         // Notification callback
  const accounts = ref(null)                // List of accounts 
  const showSettings = ref(false)           // True if showing settings dialog

  onBeforeMount(function() {
    utils.setNavPosition('top')
    updateAccounts()
  })

  // Avg Accounts
  // Computes sum [key] across all accounts
  const avgAccounts = function(key) {
    if (!accounts.value) { return 0 }
    return sumAccounts(key) / (new Date().getMonth() + 1)
  }

  // Sum Accounts
  // Computes avg [key] / current month num across all accounts
  const sumAccounts = function(key) {
    if (!accounts.value) { return 0 }
    return accounts.value.reduce(function(total, account) {
      return total + parseFloat(account.summary[key] || 0)
    }, 0)
  }
  
  // Update Accounts
  // Update the account list in the side panel
  const updateAccounts = async function() {
    var {data} = await api.Budget.listAccounts()
    accounts.value = data.items
  }

  // Upload
  // Import new transactions to the database
  const upload = async function(event, formdata) {
    if (event.shiftKey) { formdata.append('safe', true) }
    var {data} = await api.Budget.importTransactions(formdata)
    for (var item of data) {
      var title = `${item.account.name} Transactions Imported`
      var message = item.created == 0 ? 'No transactions imported.' :
        `${item.created} transactions imported from ${item.mindate} to ${item.maxdate}.
         ${item.categorized} transactions categorized.`
      notify(title, message, 'mdi-check')
    }
  }
</script>

<style>
  #budget {
    .sidepanel-panel .subitem {
      .name { float: left; }
      .balance { text-align: right; }
      .lastupdate { font-size:9px; color:var(--fgcolor40);}
    }

    td.positive .tdwrap { color: var(--lightbg-green2); font-weight:bold !important; }
    td.zero .tdwrap { color: #8889; }
    td.lowest .tdwrap { color: var(--lightbg-red1); }
  }
</style>
