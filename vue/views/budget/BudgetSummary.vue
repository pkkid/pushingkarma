<template>
  <div id='summary'>
    <div class='metrics'>
      <!-- Period -->
      <div class='metric period'>
        <div class='label'>
          <i class='icon mdi mdi-filter-variant'/>
          <div class='name'>Period</div>
        </div>
        <div class='value'>{{summary?.period}}</div>
        <div class='subtext'>
          <a v-if='!isalltime' href='?'>all-time</a>
          <span v-else>all-time</span>
        </div>
      </div>
      <!-- Wages -->
      <div class='metric wages'>
        <div class='label'>
          <i class='icon mdi mdi-cash-plus'/>
          <div class='name'>Wages</div>
        </div>
        <div class='value'>{{utils.usd(summary?.wages)}}</div>
        <div class='subtext'>{{utils.usd(summary?.wages_count)}} payments</div>
      </div>
      <!-- Spending -->
      <div class='metric spending'>
        <div class='label'>
          <i class='icon mdi mdi-cash-minus'/>
          <div class='name'>Spending</div>
        </div>
        <div class='value'>{{utils.usd(summary?.spending)}}</div>
        <div class='subtext'>{{utils.intComma(summary?.spending_count)}} transactions</div>
      </div>
      <!-- Net -->
      <div class='metric net'>
        <div class='label'>
          <i class='icon mdi mdi-cash-refund'/>
          <div class='name'>Net</div>
        </div>
        <div class='value'>{{utils.usd(summary?.net)}}</div>
        <div class='subtext'>&nbsp;</div>
      </div>
      <!-- Saved -->
      <div class='metric saved'>
        <div class='label'>
          <i class='icon mdi mdi-piggy-bank-outline'/>
          <div class='name'>Saved</div>
        </div>
        <div class='value'>{{utils.usd(summary?.saved)}}</div>
        <div class='subtext'>{{utils.percent(summary?.saved_percent)}}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {computed} from 'vue'
  import {utils} from '@/utils'
  const props = defineProps({
    summary: {type:Object, default:null},
  })
  const isalltime = computed(() => {
    return !location.search || location.search.includes('all-time')
  })
</script>

<style>
  #summary {
    .metrics {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 20px;
      padding: 10px 0px 25px 0px;
      .metric {
        padding: 10px;
        border-radius: 5px;
        background-color: var(--lightbg-bg1);
        box-shadow: 0 1px 2px 0 #0002, 0 1px 3px 1px #0001;
        .label {
          display: flex;
          align-items: center;
          font-size: 13px;
          color: var(--lightbg-fg2);
          .icon {
            font-size: 14px;
            margin-right: 6px;
          }
        }
        .value {
          font-size: 18px;
          font-weight: bold;
          color: var(--lightbg-fg0);
          padding: 3px 0px;
        }
        .subtext {
          font-size: 12px;
          color: var(--lightbg-fg4);
          a, a:visited {
            color: var(--lightbg-fg4);
            text-decoration: underline;
            text-decoration-style: dotted;
            text-decoration-thickness: 1px;
            &:hover { color: var(--lightbg-blue1); }
          }
        }
      }
    }
  }
</style>