<template>
  <LayoutPaper id='yearoverview' width='1250px'>
    <template #content>
      <!-- Search -->
      <div class='searchwrap'>
        <input type='text' v-model='_search' placeholder='Search Transactions'
          class='searchinput' @keydown.enter='search=_search || null'>
        <transition name='fade'>
          <i v-if='_search?.length' class='mdi mdi-close' @click='search=""; _search=""'/>
        </transition>
      </div>
      <!-- Header -->
      <h1>Budget Year Overview
        <div v-if='summary?.items' class='subtext'>Showing {{summary?.items.length}} categories</div>
        <div v-else class='subtext'>Loading summary...</div>
      </h1>
      <!-- Year Overview Table -->
      <div v-if='summary?.items?.length > 0'>
        <EditTable ref='edittable' v-if='summary?.items && columns' :columns='columns' :items='summary?.items'
          :footer='footer' :onRequestDeselect='onRequestDeselect' @itemSelected='onItemSelected' />
        <BudgetYearPopover ref='popover' />
      </div>
      <!-- Empty State -->
      <div v-else class='empty'>
        <i class='mdi mdi-table-search'/>
        No transactions found.
      </div>
    </template>
  </LayoutPaper>
</template>

<script setup>
  import {computed, onMounted, ref, watch, watchEffect} from 'vue'
  import {BudgetYearPopover} from '@/views/budget'
  import {EditTable, LayoutPaper} from '@/components'
  import {useUrlParams} from '@/composables'
  import {api, utils} from '@/utils'

  var cancelctrl = null                       // Cancel controller
  const loading = ref(false)                  // True to show loading indicator
  const {search} = useUrlParams({search:{}})  // Method & path url params
  const _search = ref(search.value)           // Temp search before enter
  const summary = ref(null)                   // Summary of transactions
  const columns = ref(null)                   // EditTable columns
  const edittable = ref(null)                 // Ref to EditTable component
  const popover = ref(null)                   // Ref to popover component

  // On Mounted
  // Update transactions and initialize hotkeys
  onMounted(function() { updateSummary() })

  // Watch Search
  // Update transactions and _search.value
  watch(search, function() {
    _search.value = search.value
    updateSummary()
  })

  // Watch Summary
  // Update columns when summary changes
  watch(summary, function() {
    if (summary.value?.items == 0) { columns.value = null; return }
    columns.value = [{
        name:'category', title:'Category', editable:false,
        html: cat => cat.name,
      }, ...Array.from({length:13}, (_, i) => {
        var month = utils.newDate(summary.value.minmonth)
        month.setMonth(month.getMonth() + 12 - i)
        var key = utils.formatDate(month, 'YYYY-MM-DD')
        var name = `month month-${utils.formatDate(month, 'YYYYMMDD')}`
        var title = utils.formatDate(month, 'MMM')
        return {
          name, title,
          editable: true,
          subtext: utils.formatDate(month, 'YYYY'),
          html: cat => utils.usd(cat.months[key], 0, '$', 3),
          class: cat => [getSign(cat, key), clsLowest(cat, key)].join(' '),
          _month: month,
        }
      }),{
        name:'average', title:'Average', editable:false,
        html: cat => utils.usd(averageValues(cat.months), 0, '$', 3),
      },{
        name:'total', title:'Total', editable:false,
        html: cat => utils.usd(sumValues(cat.months), 0, '$', 3),
      }
    ]
  })

  // Footer
  // Create the table footer item object
  const footer = computed(function() {
    if (!summary.value?.items) { return null }
    var item = {name:'Total', months:{}}
    var months = new Set(summary.value.items.flatMap(cat => Object.keys(cat.months)))
    months.forEach(month => {
      item.months[month] = summary.value.items.reduce(
        (sum, cat) => sum + (Number(cat.months[month]) || 0), 0)
    })
    return item
  })

  // Class Sign Determination
  // returns positive, zero, or negative depending on the value
  const getSign = function(cat, key) {
    return utils.getSign(Number(cat.months[key]) || 0)
  }

  // Class Lowest
  // returns 'lowest' if this is the lowest value in this category
  // and there are no other values 
  const clsLowest = function(cat, key) {
    var val = Number(cat.months[key]) || 0
    if (val >= 0) { return '' }
    var vals = Object.values(cat.months).map(Number).filter(Number.isFinite)
    var lowest = Math.min(...vals)
    var lowestCount = vals.filter(v => v == lowest).length
    return lowestCount == 1 && lowest == val ? 'lowest' : ''
  }
  
  // Average Values
  // Calculate the average of the values in the object
  const averageValues = function(obj) {
    var vals = Object.values(obj).map(Number).filter(Number.isFinite)
    return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0
  }

  // Sum Values
  // Calculate the sum of the values in the object
  const sumValues = function(obj) {
    var vals = Object.values(obj).map(Number).filter(Number.isFinite)
    return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0)) : 0
  }

  // On Selected
  // Handle item selected event
  const onItemSelected = function(event, row, col, editing) {
    if (editing || (popover.value.showing() && event.key?.includes('Arrow'))) {
      var month = columns.value[col]._month
      var {id, name} = summary.value.items[row]
      var category = {id, name}
      var cell = edittable.value.getCell(row, col)
      popover.value.show(cell, category, month, search.value)
    } else {
      popover.value.hide()
    }
  }

  // On Deselected
  // Handle item deselected event. Will capture the edittable esc
  // keyevent and not deselect the cell if the popover is showing.
  const onRequestDeselect = function(event, row, col, editing) {
    if (popover.value.showing()) { popover.value.hide(); return false }
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
    position: relative;

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
      .tdwrap { font-size:12px; }
      .category { width:151px; text-align:left; .tdwrap { background-color: #ddd8; }}
      .month { width:69px; text-align:right; .tdwrap { font-family:var(--fontfamily-code); font-size:11px; }}
      .average { width:69px; text-align:right; .tdwrap { font-family:var(--fontfamily-code); font-size:11px; background-color: #ddd8; }}
      .total { width:69px; text-align:right; .tdwrap { font-family:var(--fontfamily-code); font-size:11px; background-color: #ddd8; }}
    }
  }
</style>
