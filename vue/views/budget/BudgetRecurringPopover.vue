<template>
  <div v-if='showing' ref='root' id='budgetrecurringpopover' class='lightbg'>
    <h3>
      {{item?.name}}
      <div class='subtext'>{{item?.count}} transactions</div>
    </h3>
    <div v-if='trxs?.items?.length'>
      <div class='trxs' :class='{scroll}'>
        <table>
          <tr v-for='(trx, index) in trxs?.items' :key='index'>
            <td class='date'><div class='tdwrap'>{{utils.formatDate(trx.date, 'MMM D, YYYY')}}</div></td>
            <td class='payee'><div class='tdwrap'>{{trx.payee}}</div></td>
            <td class='amount'><div class='tdwrap'>{{utils.usd(trx.amount, 0, '$', 3)}}</div></td>
          </tr>
        </table>
      </div>
      <div class='budgetrecurringpopover-footer'>
        <router-link :to='`/budget?search=${searchstr}`'>{{trxs.items?.length}} transactions</router-link>
        <div class='total' :class='utils.getSign(total)'>{{utils.usd(total, 0, '$', 3)}}</div>
      </div>
    </div>
    <div v-else>
      <div v-if='item?.reasons?.length' class='reasons'>
        <div v-for='(reason, index) in item.reasons' :key='index'>{{reason}}</div>
      </div>
      <div style='margin-bottom:20px;'>No transactions to display.</div>
    </div>
  </div>
</template>

<script setup>
  import {computed, nextTick, ref} from 'vue'
  import {api, utils} from '@/utils'

  var cancelctrl = null             // Cancel controller
  const root = ref(null)            // Reference to root element
  const loading = ref(false)        // True to show loading indicator
  const showing = ref(false)        // True if the popover is showing
  const trxs = ref(null)            // Transactions to show
  const item = ref(null)            // Recurring item to show
  const scroll = ref(false)         // True if .trxs has scrollbar

  // Search String
  // Search string for the transactions
  const searchstr = computed(function() {
    if (!item.value) { return '' }
    var str = ``
    for (var word of item.value.name.split(' ')) {
      str += ` payee:${word}`
    }
    str += ` date>${utils.formatDate(item.value.first_date, 'YYYY-MM-DD')}`
    return str.trim()
  })

  // Total
  // Sum the values in the object
  const total = computed(function() {
    if (!trxs.value?.items) { return 0 }
    return trxs.value.items.reduce(function(sum, trx) {
      return sum + Number(trx.amount)
    }, 0)
  })

  // Set Position
  // Set the position of the popover
  const setPosition = async function(cell) {
    if (!showing.value) { return }
    await nextTick()
    var prect = cell.$el.closest('#recurring article').getBoundingClientRect()
    var crect = cell.$el.getBoundingClientRect()
    var left = crect.left - prect.left
    var top = crect.top - prect.top + crect.height + 5
    root.value.style.left = `${left}px`
    root.value.style.top = `${top}px`
    const elem = root.value?.querySelector('.trxs')
    scroll.value = elem?.scrollHeight > elem?.clientHeight
  }

  // Show Popover
  // Show the popover with the given item
  const show = async function(cell, _item) {
    item.value = _item
    showing.value = true
    await updateTransactions()
    setPosition(cell)
  }

  // Hide Popover
  // Hide the popover
  const hide = function() {
    showing.value = false
    trxs.value = null
    item.value = null
    scroll.value = false
    cancelctrl = api.cancel(cancelctrl)
  }

  // Update Transactions
  // Fetch transactions from the server
  const updateTransactions = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search:searchstr.value}
      var {data} = await api.Budget.listTransactions(params, cancelctrl.signal)
      trxs.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      loading.value = false
    }
  }

  // Define Exposed
  // Expose this function to the parent
  defineExpose({
    show, hide,
    showing: () => showing.value,
  })
</script>

<style>
  #budgetrecurringpopover {
    border-radius: 4px;
    border: 1px solid var(--lightbg-bg4);
    box-shadow: 0 1px 3px 0 #3c40434d, 0 4px 8px 3px #3c404326;
    max-height: 300px;
    min-height: 50px;
    font-size: 12px;
    overflow: hidden;
    padding: 10px;
    position: absolute;
    width: 320px;
    z-index: 1;

    h3 {
      margin-top: 0px;
      position: relative;
      margin-right: 25px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      .subtext { margin-top: -7px; }
      &::before {
        background-color: #d65d0e;
        bottom: -3px;
        content: ' ';
        display: block;
        height: 1px;
        position: absolute;
        width: 70px;
      }
    }

    .trxs {
      max-height: 150px;
      overflow-y: auto;
    }

    table {
      border-collapse: collapse;
      border-spacing: 0;
      font-size: 10px;
      width: 100%;
      table-layout: fixed;

      .tdwrap {
        width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.2;
      }
      .date { width: 80px; }
      .payee { padding:0px 8px; }
      .amount, .total { width:55px; text-align:right; font-family:var(--fontfamily-code); padding-right:5px; }
    }

    .total {
      border-top: 1px solid color-mix(in srgb, var(--lightbg-fg4), #0000 50%);
      text-align: right;
      float: right;
      margin: 3px 5px 0px 0px;
      font-size: 10px;
      font-weight: bold;
      line-height: 1.8;
      font-family:var(--fontfamily-code);
      &.negative { color: var(--lightbg-red1); }
      &.positive { color: var(--lightbg-green2); }
    }
    .trxs.scroll + .reasons + .budgetrecurringpopover-footer,
    .trxs.scroll + .budgetrecurringpopover-footer {
      margin-right: 11px;
    }

    .budgetrecurringpopover-footer {
      font-size: 10px;
      margin-top: 5px;
      margin-left: 2px;
    }
  }
</style>
