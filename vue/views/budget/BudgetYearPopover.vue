<template>
  <div v-if='showing' ref='root' id='budgetyearpopover' class='lightbg'>
    Hi Mom!
  </div>
</template>

<script setup>
  import {nextTick, onMounted, ref} from 'vue'
  import {api, utils} from '@/utils'

  var cancelctrl = null             // Cancel controller
  const root = ref(null)            // Reference to root element
  const loading = ref(false)        // True to show loading indicator
  const showing = ref(false)        // True if the popover is showing
  const trxs = ref(null)            // Transactions to show
  const category = ref(null)        // Category to show

  // On Mounted
  onMounted(function() {
    console.log('Popover mounted')
  })

  // Show Popover
  // Show the popover with the given category and month
  const show = async function(cell, category, month, search) {
    console.log(`show(${category.name}, ${utils.formatDate(month, 'YYYY-MM-DD')}, "${search}")`)
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
    category.value = category
    updateTransactions(category, month, search)
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
  const updateTransactions = async function(category, month, search) {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var maxdate = new Date(month)
      maxdate.setMonth(maxdate.getMonth() + 1)
      search = search || ''
      search += ` category="${category.value.name}"`
      search += ` date>=${utils.formatDate(month, 'YYYY-MM-DD')}`
      search += ` date<${utils.formatDate(maxdate, 'YYYY-MM-DD')}`
      var {data} = await api.Budget.listTransactions({search:search.trim()}, cancelctrl.signal)
      trxs.value = data
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
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
    width: 150px;
    min-height: 50px;
    max-height: 300px;
    border: 2px solid red;
    top: 0px;
    left: 0px;
    z-index: 99;
  }
</style>
