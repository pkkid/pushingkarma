<template>
  <div id='budget'>
    <LayoutSidePanel>
      <!-- Side Panel (Navigation) -->
      <template #panel>
        <div class='menu'>
          <div class='item link' @click="view=''">
            <i class='mdi mdi-credit-card-outline'/>
            Transactions
          </div>
          <div class='subitem account'>
            <div class='name'>Bank 2 Balance</div>
            <div class='balance'>$1</div>
            <div class='lastupdate'>Updated 1 week ago</div>
          </div>
          <div class='subitem account'>
            <div class='name'>Bank 1 Balance</div>
            <div class='balance'>$2</div>
            <div class='lastupdate'>Updated 3 days ago</div>
          </div>
          <div class='item link' @click="view='year'">
            <i class='mdi mdi-checkbook'/>
            Year Overview
          </div>
          <div class='subitem account'>
            <div class='name'>Total Spent 2025</div>
            <div class='balance'>$2</div>
            <div class='lastupdate'>Average $123 / month</div>
          </div>
          <div class='subitem account'>
            <div class='name'>Total Saved 2025</div>
            <div class='balance'>$2</div>
            <div class='lastupdate'>Average $124 / month</div>
          </div>
          <div class='item link' @click='showSettings=true'>
            <i class='mdi mdi-cog'/>
            Settings
          </div>
        </div>
      </template>
      <!-- Content -->
      <template #content>
        <Dropzone @filesDropped='upload'>
          <BudgetYear v-if="view=='year'" />
          <BudgetTransactions v-else />
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

  const showSettings = ref(false)
  const {view} = useUrlParams({view:{}})
  const {notify} = inject('notify')

  onBeforeMount(function() { utils.setNavPosition('top') })

  // Upload
  // Import new transactions to the database
  const upload = async function(formdata) {
    // var {data} = await api.Budget.upload(formdata)
    // var title = `${data.account} Import`
    // var message = 'No new transactions found.'
    // if (data.transactions > 0) {
    //   message = `${data.transactions} transactions imported.`
    //   if (data.categorized > 0) { message += ` ${data.categorized} have been categorized.` }
    //   if (data.labeled > 0) { message += ` ${data.labeled} have been labeled.` }
    // }
    console.log('Sending notification..')
    notify('Hi Mom!')
    // this.$root.$emit('notify', title, message, 'mdi-check')
  }
</script>

<style>
  .sidepanel-panel .subitem {
    .name { float: left; }
    .balance { text-align: right; }
    .lastupdate { font-size:9px; color:var(--fgcolor40);}
  }
</style>
