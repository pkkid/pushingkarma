<template>
  <div id='budget'>
    <LayoutSidePanel>
      <!-- Side Panel (Navigation) -->
      <template #panel>
        <div class='menu'>
          <!-- Transactions -->
          <div class='item link' @click="view=''">
            <i class='mdi mdi-credit-card-outline'/>
            Transactions
          </div>
          <template v-for='account in accounts' :key='account.id'>
            <div v-if='!account.rules?.hidden' class='subitem account'>
              <div class='name'>{{account.name}} Balance</div>
              <div class='balance'>{{utils.usd(account.balance, places=0)}}</div>
              <div class='lastupdate'>Updated {{utils.formatDate(account.balance_updated, '')}}</div>
            </div>
          </template>
          <!-- Year Overview -->
          <div class='item link' @click="view='year'">
            <i class='mdi mdi-checkbook'/>
            Year Overview
          </div>
          <div class='subitem account'>
            <div class='name'>Total Spent {{utils.formatDate(new Date(), 'YYYY')}}</div>
            <div class='balance'>{{utils.usd(totalspent, places=0)}}</div>
            <div class='lastupdate'>Average {{utils.usd(averagespent, places=0)}} / month</div>
          </div>
          <div class='subitem account'>
            <div class='name'>Total Saved {{utils.formatDate(new Date(), 'YYYY')}}</div>
            <div class='balance'>{{utils.usd(totalsaved, places=0)}}</div>
            <div class='lastupdate'>Average {{utils.usd(averagesaved, places=0)}} / month</div>
          </div>
          <div class='item link' @click='showSettings=true'>
            <i class='mdi mdi-cog'/>
            Settings
          </div>
        </div>
      </template>
      <!-- Content -->
      <template #content>
        <Dropzone @filesDropped='upload' text='Drop Transactions' subtext='Hold shift for safe import'>
          <BudgetYear v-if="view=='year'" />
          <BudgetTransactions v-else />
        </Dropzone>
      </template>
    </LayoutSidePanel>
  </div>
  <BudgetSettings :visible='showSettings' @close='showSettings=false'/>
</template>

<script setup>
  import {computed, inject, onBeforeMount, ref} from 'vue'
  import {BudgetSettings, BudgetTransactions, BudgetYear} from '@/views/budget'
  import {LayoutSidePanel} from '@/components/Layout'
  import {Dropzone} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'

  const {view} = useUrlParams({view:{}})    // Current view
  const {notify} = inject('notify')         // Notification callback
  const accounts = ref(null)                // List of accounts 
  const showSettings = ref(false)           // True if showing settings dialog

  onBeforeMount(function() {
    utils.setNavPosition('top')
    updateAccounts()
  })

  // Total Spent
  // Computes total amount spent this year across all accounts
  const totalspent = computed(function() {
    if (!accounts.value) return 0
    return accounts.value.reduce(function(total, account) {
      var spent = account.summary?.spend_this_year || 0
      return total + spent
    }, 0)
  })

  // Total Saved
  // Computes total saved spent this year across all accounts
  const totalsaved = computed(function() {
    if (!accounts.value) return 0
    return accounts.value.reduce(function(total, account) {
      var income = account.summary?.income_this_year || 0
      var spent = account.summary?.spend_this_year || 0
      return total + spent + income
    }, 0)
  })

  // Average Spent
  // Computes total amount spent this year across all accounts
  const averagespent = computed(function() {
    if (!accounts.value) return 0
    return accounts.value.reduce(function(total, account) {
      var spent = account.summary?.avg_spend_per_month_this_year || 0
      return total + spent
    }, 0)
  })

  // Average Saved
  // Computes total saved spent this year across all accounts
  const averagesaved = computed(function() {
    if (!accounts.value) return 0
    return accounts.value.reduce(function(total, account) {
      var income = account.summary?.avg_income_per_month_this_year || 0
      var spent = account.summary?.avg_spend_per_month_this_year || 0
      return total + spent + income
    }, 0)
  })
  
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
  .sidepanel-panel .subitem {
    .name { float: left; }
    .balance { text-align: right; }
    .lastupdate { font-size:9px; color:var(--fgcolor40);}
  }
</style>
