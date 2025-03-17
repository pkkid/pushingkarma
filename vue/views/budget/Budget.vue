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
          <div class='item link' @click="view='settings'">
            <i class='mdi mdi-cog'/>
            Settings
          </div>
        </div>
      </template>
      <!-- Content -->
      <template #content>
        <BudgetSettings v-if="view=='settings'" />
        <BudgetYear v-if="view=='year'" />
        <BudgetTransactions v-else />
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {inject, onBeforeMount, ref} from 'vue'
  import {utils} from '@/utils'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'
  import BudgetTransactions from '@/views/budget/BudgetTransactions.vue'
  import BudgetYear from '@/views/budget/BudgetYear.vue'
  import BudgetSettings from '@/views/budget/BudgetSettings.vue'

  const {view} = useUrlParams({
    view: {type:String},
  })

  onBeforeMount(function() { utils.setNavPosition('top') })
</script>
