<template>
  <LayoutPaper id='yearoverview' width='1250px'>
    <template #content>
      <!-- Search -->
      <div class='searchwrap'>
        <input type='text' v-model='_search' placeholder='Search Transactions'
          class='searchinput' @keydown.enter='search=_search'>
        <transition name='fade'>
          <i v-if='_search?.length' class='mdi mdi-close' @click='search=""; _search=""'/>
        </transition>
      </div>
      <!-- Header -->
      <h1>Budget Year Overview
        <div v-if='summary?.items' class='subtext'>Showing {{summary?.items.length}} categories</div>
        <div v-else class='subtext'>Loading summary...</div>
      </h1>
      <!-- Year Overview -->
      <EditTable ref='edittable' v-if='summary?.items && columns' :columns='columns'
        :items='summary?.items' @itemSelected='onItemSelected' />
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {computed, onMounted, ref, watch, watchEffect} from 'vue'
  import {EditTable, LayoutPaper} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'

  var cancelctrl = null                       // Cancel controller
  const loading = ref(false)                  // True to show loading indicator
  const {search} = useUrlParams({search:{}})  // Method & path url params
  const _search = ref(search.value)           // Temp search before enter
  const summary = ref(null)                   // Summary of transactions

  // On Mounted
  // Update transactions and initialize hotkeys
  onMounted(function() {
    updateSummary()
  })

  // Watch Search
  // Update transactions and _search.value
  watch(search, function() { updateSummary() })
  watchEffect(() => _search.value = search.value)

  // Computed Columns
  // Update columns when summary changes
  const columns = computed(function() {
    if (!summary.value?.items) { return null }
    var cols = []
    // Category Column
    cols.push({
      name:'category', title:'Category', editable:false,
      html: cat => cat.name,
    })
    // Month Columns
    var month = utils.newDate(summary.value.minmonth)
    for (var i=0; i<12; i++) {
      var key = utils.formatDate(month, 'YYYY-MM-DD')
      cols.push((function(mon, key) {
        return {
          name: `month month-${utils.formatDate(mon, 'YYYYMMDD')}`,
          title: utils.formatDate(mon, 'MMM'),
          editable: true,
          html: cat => utils.usd(cat.months[key], 0),
        }
      })(month, key))
      month.setMonth(month.getMonth() + 1)
    }
    // Average and Total Columns
    cols.push({
      name:'average', title:'Average', editable:false,
      html: cat => utils.usd(averageValues(cat.months), 0),
    })
    cols.push({
      name:'total', title:'Total', editable:false,
      html: cat => utils.usd(sumValues(cat.months), 0),
    })
    return cols
  })

  // Average Values
  // Calculate the average of the values in the object
  const averageValues = function(obj) {
    var vals = Object.values(obj).map(v => parseFloat(v)).filter(v => Number.isFinite(v))
    if (!vals.length) { return 0 }
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
  }

  // Sum Values
  // Calculate the sum of the values in the object
  const sumValues = function(obj) {
    var vals = Object.values(obj).map(v => parseFloat(v)).filter(v => Number.isFinite(v))
    if (!vals.length) { return 0 }
    return Math.round(vals.reduce((a, b) => a + b, 0))
  }

  // On Selected
  // Handle item selected event
  const onItemSelected = function(event, row, col, editing) {
    console.log(`onItemSelected(event, row=${row}, col=${col}, editing=${editing})`)
  }

  // Update Summary
  // Fetch summary from the server
  const updateSummary = async function() {
    loading.value = true
    cancelctrl = api.cancel(cancelctrl)
    try {
      var params = {search:search.value}
      var {data} = await api.Budget.summarizeMonths(params, cancelctrl.signal)
      summary.value = data
      // edittable.value?.deselect(null, false)
      // edittable.value?.clearUndoRedoStack()
    } catch (err) {
      if (!api.isCancel(err)) { throw(err) }
    } finally {
      setTimeout(() => loading.value = false, 500)
    }
  }

</script>

<style>
  #yearoverview {
    .searchwrap {
      text-align: right;
      display: flex;
      justify-content: flex-end;
      margin-top: -10px;
      align-items: center;
      padding-top: 22px;
      float: right;
      width: 550px;
      input {
        width: 100%;
        border-radius: 20px;
        padding: 5px 15px;
      }
      .mdi-close {
        position: absolute;
        right: 40px;
        font-size: 14px;
      }
    }

    .edittable {
      .tdwrap { font-size: 12px; }
      .category { width:132px; }
      .month { width:72px; text-align:right;  }
      .average { width:80px; text-align:right;  }
      .total { width:80px; text-align:right;  }
      td .category { background-color:#bbb2; }
      td .month { font-family:var(--fontfamily-code); font-size:11px; }
      td .average { font-family:var(--fontfamily-code); font-size:11px; background-color:#bbb2;  }
      td .total { font-family:var(--fontfamily-code); font-size:11px; background-color:#bbb2;  }
    }
  }
</style>
