<template>
  <LayoutPaper id='recurring' width='1000px'>
    <template #content>
      <!-- Controls -->
      <div class='controls'>
        <ToggleSwitch v-model='includeinactive' label='Include Inactive' />
      </div>
      <!-- Header -->
      <h1>
        Budget Recurring
        <div v-if='summary' class='subtext'>
          {{utils.intComma(summary.count)}} detected -
          {{utils.usd(summary.monthly_total)}}/mo -
          {{utils.usd(summary.yearly_total)}}/yr
        </div>
        <div v-else class='subtext'>Loading recurring items...</div>
      </h1>
      <!-- Table -->
      <div v-if='summary?.items?.length'>
        <EditTable ref='edittable' :columns='COLUMNS' :items='summary.items'
          :onRequestDeselect='onRequestDeselect' @itemSelected='onItemSelected'/>
        <BudgetRecurringPopover ref='popover'/>
      </div>
      <IconMessage v-else-if='loading' icon='pk' iconsize='40px' animation='gelatine' text='Detecting recurring items' ellipsis/>
      <IconMessage v-else icon='mdi-robot-angry-outline' iconsize='40px' text='No recurring items detected.' />
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {onMounted, ref, watch} from 'vue'
  import {EditTable, IconMessage, LayoutPaper, ToggleSwitch} from '@/components'
  import {useStorage} from '@/composables'
  import {api, utils} from '@/utils'
  import BudgetRecurringPopover from './BudgetRecurringPopover.vue'

  const accountIcons = function(item) {
    return item.accounts.map(function(name) {
      var path = `/static/img/icons/${name.toLowerCase()}.svg`
      return `<i class='icon' style='--mask:url(${path})' title='${utils.escapeHtml(name)}'/>` 
    }).join('')
  }

  const COLUMNS = [{
      name:'accounts', title:'Act', editable:false,
      html: item => accountIcons(item),
      tooltip: item => utils.escapeHtml(item.accounts.join(', ')),
    },{
      name:'payee', title:'Payee', editable:true,
      html: item => `${item.name.split('|')[0].toUpperCase()}<div class='subtext'>${item.categories.join("; ")}</div>`,
    },{
      name:'cadence', title:'Cadence', editable:false,
      html: item => `${utils.title(item.cadence)}<div class='subtext'>${item.is_active ? `Active` : 'Inactive'}</span>`,
    },{
      name:'lastdate', title:'Last', editable:false,
      html: item => `${utils.formatDate(item.last_date, 'MMM D, YYYY')}<div class='subtext'>${item.last_date} days ago</div>`,
    },{
      name:'monthly', title:'Monthly', editable:false,
      html: item => item.cadence == 'monthly' ? utils.usd(item.last_amount) : '--',
      class: item => item.cadence == 'monthly' ? '' : 'dimmed',
    },{
      name:'yearly', title:'Yearly', editable:false,
      html: item => item.cadence == 'monthly' ? utils.usd(item.last_amount*12) : utils.usd(item.last_amount),
    }

    // {
    //   name:'confidence', title:'Conf', editable:false,
    //   class: item => item.confidence >= 80 ? 'high' : item.confidence >= 60 ? 'medium' : 'low',
    //   html: item => String(item.confidence),
    // },,,,
  ]

  var cancelctrl = null               // Cancel controller
  const loading = ref(false)          // True while loading recurring items
  const summary = ref(null)           // Summary of recurring items
  const includeinactive = useStorage('budget.inactive', false)   // Include inactive items in summary
  const edittable = ref(null)         // Ref to the recurring table
  const popover = ref(null)           // Ref to the recurring payee popover

  // On Mounted & Watchers
  // Update recurring items when mounted, and when toggles change
  onMounted(function() { updateRecurring() })
  watch(includeinactive, function() { updateRecurring() })

  // On Selected
  // Match the year view: open on edit/enter, and keep the popover in sync while
  // navigating with arrows.
  const onItemSelected = function(event, row, col, editing) {
    if (col != 1) {
      popover.value.hide()
      return
    }
    if (editing || (popover.value.showing() && event.key?.includes('Arrow'))) {
      var item = summary.value.items[row]
      var cell = edittable.value.getCell(row, col)
      popover.value.show(cell, item)
    } else {
      popover.value.hide()
    }
  }

  // On Request Deselect
  // Keep the cell selected while the popover is visible so Escape can close it.
  const onRequestDeselect = function() {
    if (popover.value.showing()) {
      popover.value.hide()
      return false
    }
  }

  // Update Recurring
  // Load recurring items from API with current toggle settings.
  const updateRecurring = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {
        include_inactive: includeinactive.value,
        min_confidence: 45,
        lookback_days: 913,
      }
      var {data} = await api.Budget.listRecurring(params, cancelctrl.signal)
      summary.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }
</script>

<style>
  #recurring {
    .controls {
      float: right;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      gap: 1px;
      margin: -6px 0 12px 0;
      width: 140px;
    }

    .edittable {
      .tdwrap {
        display: flex;
        height: 42px;
        .fakeinput {
          padding-top: 5px;
          line-height: 16px;
          height: 42px !important;
        }
      }

      .accounts { width: 36px; text-align: center; }
      .accounts .tdwrap {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        .icon {
          background-color: var(--lightbg-fg4);
          display: inline-block;
          height: 16px;
          mask: var(--mask) no-repeat center / contain;
          position: relative;
          top: 3px;
          width: 16px;
        }
      }
      .payee { width: 350px; text-align: left; .tdwrap { max-width:350px; } }
      .confidence { width: 100px; text-align: right; }
      .cadence { width: 100px; text-align: right; }
      .lastdate { width: 130px; text-align: right; }
      .monthly { width: 110px; text-align: right; }
      .yearly { width: 110px; text-align: right; }
      .status { width: 110px; text-align: left; }

      td.high .tdwrap { color: var(--lightbg-green2); }
      td.medium .tdwrap { color: #b67f00; }
      td.low .tdwrap { color: var(--lightbg-red1); }
      .dimmed { opacity: 0.5;  }
    }
  }
</style>
