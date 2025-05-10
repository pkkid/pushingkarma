<template>
  <div v-if='showing' ref='root' id='budgetyearpopover' class='lightbg'>
    {{category?.name}}
    <div class='subtext'>{{utils.formatDate(month, 'MMMM YYYY')}}</div>
    <table v-if='trxs'>
      <tbody>
        <tr v-for='(trx, index) in trxs?.items' :key='index'>
          <td class='date'>{{utils.formatDate(trx.date, 'M/D') }}</td>
          <td class='payee'>{{trx.payee}}</td>
          <td class='amount'>{{trx.amount}}</td>
        </tr>
      </tbody><tfoot><tr>
        <td colspan='2'></td>
        <td class='total'>total</td>
      </tr></tfoot>
    </table>
  </div>
</template>

<script setup>
  import {nextTick, onMounted, ref} from 'vue'
  import {LoadingIcon} from '@/components'
  import {api, utils} from '@/utils'

  var cancelctrl = null             // Cancel controller
  const root = ref(null)            // Reference to root element
  const loading = ref(false)        // True to show loading indicator
  const showing = ref(false)        // True if the popover is showing
  const trxs = ref(null)            // Transactions to show
  const category = ref(null)        // Category to show
  const month = ref(null)           // Month to show

  // Show Popover
  // Show the popover with the given category and month
  const show = async function(cell, cat, mon, search) {
    // console.log(`show(${category.name}, ${utils.formatDate(month, 'YYYY-MM-DD')}, "${search}")`)
    category.value = cat
    month.value = mon
    showing.value = true
    await nextTick()
    // Set the top position of the popover
    var winheight = document.documentElement.clientHeight
    var cellrect = cell.$el.getBoundingClientRect()
    var top = cellrect.top - 55
    var left = cellrect.right - 150
    root.value.style.top = `${top}px`
    root.value.style.left = `${left}px`
    // Populate the popover contents
    updateTransactions(cat, mon, search)
  }

  // Hide Popover
  // Hide the popover
  const hide = function() {
    showing.value = false
    trxs.value = null
    category.value = null
  }

  // Update Transactions
  // Fetch transactions from the server
  const updateTransactions = async function(cat, mon, search) {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var maxdate = new Date(mon)
      maxdate.setMonth(maxdate.getMonth() + 1)
      search = search || ''
      search += ` category="${cat.name}"`
      search += ` date>=${utils.formatDate(mon, 'YYYY-MM-DD')}`
      search += ` date<${utils.formatDate(maxdate, 'YYYY-MM-DD')}`
      var {data} = await api.Budget.listTransactions({search:search.trim()}, cancelctrl.signal)
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
  #budgetyearpopover {
    position: fixed;
    width: 300px;
    min-height: 50px;
    max-height: 300px;
    top: 0px;
    left: 0px;
    z-index: 99;
    border-radius: 4px;
    box-shadow: 0 1px 3px 0 #3c40434d, 0 4px 8px 3px #3c404326;
    border: 1px solid var(--lightbg-bg4);
    overflow: hidden;

    table {
      width: 100%;
      font-size: 10px;
    }

    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 50px;
    }

  }
</style>
