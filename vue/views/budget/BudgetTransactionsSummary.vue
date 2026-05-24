<template>
  <div v-if='summary' id='budgetsummary'>
    <div class='bignums'>
      <!-- Uncategorized (filter button) -->
      <div v-if='summary.uncategorized_count' class='bignum-panel bignum-btn'
          :class='{active: isFilterActive("category=null")}'
          @click='toggleFilter("category=null")'>
        <div class='bignum-num'>{{utils.intComma(summary.uncategorized_count)}}</div>
        <div class='bignum-label'>Uncategorized</div>
      </div>
      <!-- Unapproved (filter button) -->
      <div v-if='summary.unapproved_count' class='bignum-panel bignum-btn'
          :class='{active: isFilterActive("approved=false")}'
          @click='toggleFilter("approved=false")'>
        <div class='bignum-num'>{{utils.intComma(summary.unapproved_count)}}</div>
        <div class='bignum-label'>Unapproved</div>
      </div>
      <!-- Total Income (only if nonzero) -->
      <div v-if='summary.total_count < 1000 && summary.total_income != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_income, 0, '$', 3)}}</div>
        <div class='bignum-label'>Income</div>
      </div>
      <!-- Total Spent -->
      <div v-if='summary.total_count < 1000 && summary.total_spent != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_spent, 0, '$', 3)}}</div>
        <div class='bignum-label'>Spent</div>
      </div>
      <!-- Total Amount -->
      <div v-if='summary.total_count < 1000 && summary.total_spent != 0 && summary.total_income != 0' class='bignum-panel'>
        <div class='bignum-num'>{{utils.usd(summary.total_amount, 0, '$', 3)}}</div>
        <div class='bignum-label'>Total</div>
      </div>
      <!-- Charts -->
      <BudgetChartMonthly v-if='summary.total_months >= 3'/>
      <BudgetChartTreemap v-if='summary.total_payees >= 2'/>
    </div>
  </div>
</template>

<script setup>
  import {useUrlParams} from '@/composables'
  import {utils} from '@/utils'
  import BudgetChartMonthly from './BudgetChartMonthly.vue'
  import BudgetChartTreemap from './BudgetChartTreemap.vue'

  const props = defineProps({
    summary: {type:Object, default:null},       // Summary data from parent
  })
  const {search} = useUrlParams({search:{}})    // Search string from URL

  // Is Filter Active
  // Check if the filter token is already in the search string
  const isFilterActive = function(filter) {
    return (search.value || '').split(/\s+/).includes(filter)
  }

  // Toggle Filter
  // Append or remove a filter token from the current search string
  const toggleFilter = function(filter) {
    var parts = (search.value || '').split(/\s+/).filter(p => p)
    var idx = parts.indexOf(filter)
    if (idx >= 0) { parts.splice(idx, 1) }
    else { parts.push(filter) }
    search.value = parts.join(' ') || null
  }

</script>

<style>
  #budgetsummary {
    margin-bottom: 15px;
    clear: both;

    .bignums {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 5px;
      flex-wrap: nowrap;
    }

    .bignum-panel {
      align-items: end;
      border-radius: 6px;
      border: 1px solid var(--lightbg-bg2);
      display: flex;
      flex-direction: column;
      height: 60px;
      justify-content: center;
      min-width: 80px;
      padding: 6px 14px;
      user-select: none;
      white-space: nowrap;

      .bignum-num {
        font-size: 18px;
        font-weight: 600;
        color: var(--lightbg-fg1);
        line-height: 1.2;
        text-align: right;
      }
      .bignum-label {
        font-size: 10px;
        color: var(--lightbg-fg4);
        letter-spacing: 0.04em;
        margin-top: 2px;
      }
      &.bignum-btn {
        cursor: pointer;
        transition: all 0.2s ease;
        &:hover {
          background-color: var(--lightbg-bg2);
          border-color: var(--lightbg-bg3);
        }
        &.active {
          border-color: var(--accent);
          box-shadow: inset 0 0 0 1px var(--accent);
          background-color: #f812;
        }
      }
    }

  }
</style>
