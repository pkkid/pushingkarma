<template>
  <LayoutPaper id='recurring' width='1200px'>
    <template #content>
      <h1>Budget Recurring
        <div v-if='recurringSummary' class='subtext'>
          {{utils.intComma(recurringSummary.count)}} detected
          • {{utils.usd(recurringSummary.monthly_total)}} / month
          • {{utils.usd(recurringSummary.yearly_total)}} / year
        </div>
        <div v-else class='subtext'>Loading recurring items...</div>
      </h1>
      <div class='controls'>
        <ToggleSwitch v-model='includeBills' label='Include recurring bills' />
        <ToggleSwitch v-model='includeInactive' label='Include inactive recurring items' />
      </div>
      <table v-if='recurringSummary?.items?.length' class='recurring-table'>
        <thead>
          <tr>
            <th>Payee</th>
            <th>Confidence</th>
            <th>Cadence</th>
            <th>Median</th>
            <th>Monthly</th>
            <th>Yearly</th>
            <th>Last</th>
            <th>Category</th>
            <th>Status</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for='item in recurringSummary.items' :key='item.key' :class='{inactive:item.is_stale}'>
            <td>
              <div class='payee'>{{item.display_name}}</div>
              <div class='subtext'>{{item.accounts.join(', ')}}</div>
            </td>
            <td :class='confidenceClass(item.confidence)'>{{item.confidence}}</td>
            <td>{{item.cadence}}</td>
            <td>{{utils.usd(item.median_amount)}}</td>
            <td>{{utils.usd(item.monthly_cost)}}</td>
            <td>{{utils.usd(item.yearly_cost)}}</td>
            <td>{{utils.formatDate(item.last_date, 'YYYY-MM-DD')}}</td>
            <td>{{item.category_names.join(', ') || '-'}}</td>
            <td>{{item.is_stale ? `Inactive (${item.days_since_last}d)` : 'Active'}}</td>
            <td>{{item.reasons.join(' • ')}}</td>
          </tr>
        </tbody>
      </table>
      <IconMessage v-else-if='loading' icon='pk' iconsize='40px' animation='gelatine' text='Detecting recurring items' ellipsis/>
      <IconMessage v-else icon='mdi-robot-angry-outline' iconsize='40px' text='No recurring items detected.' />
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {onMounted, ref, watch} from 'vue'
  import {IconMessage, LayoutPaper, ToggleSwitch} from '@/components'
  import {api, utils} from '@/utils'

  var cancelctrl = null
  const loading = ref(false)
  const includeBills = ref(false)
  const includeInactive = ref(true)
  const recurringSummary = ref(null)

  onMounted(function() {
    updateRecurring()
  })

  watch(includeBills, function() {
    updateRecurring()
  })

  watch(includeInactive, function() {
    updateRecurring()
  })

  const confidenceClass = function(confidence) {
    if (confidence >= 80) { return 'high' }
    if (confidence >= 60) { return 'medium' }
    return 'low'
  }

  const updateRecurring = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {
        include_bills: includeBills.value,
        include_inactive: includeInactive.value,
        min_confidence: 45,
        lookback_days: 913,
      }
      var {data} = await api.Budget.listRecurring(params, cancelctrl.signal)
      recurringSummary.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 300)
    }
  }
</script>

<style>
  #recurring {
    .controls {
      display: flex;
      justify-content: flex-end;
      gap: 16px;
      margin: -6px 0 12px 0;
    }

    .recurring-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;

      th, td {
        border-bottom: 1px solid #ddd6;
        text-align: left;
        vertical-align: top;
        padding: 8px 10px;
      }

      th {
        font-size: 11px;
        text-transform: uppercase;
        color: var(--fgcolor70);
        letter-spacing: 0.4px;
      }

      td.high { color: var(--lightbg-green2); font-weight: bold; }
      td.medium { color: #b67f00; font-weight: bold; }
      td.low { color: var(--lightbg-red1); font-weight: bold; }

      .payee { font-weight: bold; }
      .subtext { font-size: 10px; color: var(--fgcolor50); }

      tr.inactive {
        opacity: 0.72;
      }
    }
  }
</style>
