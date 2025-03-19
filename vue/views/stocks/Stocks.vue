<template>
  <div id='stocks'>
    <LayoutSidePanel>
      <!-- Search -->
      <template #panel>
        <StocksSearch :stockgroups='stockgroups' />
      </template>
      <template #content>
        <LayoutPaper width='1000px'>
          <!-- Stocks Overview -->
          <template #content>
            <h1>Stocks</h1>
            <div class='chartlayout' style='margin-top:20px;'>
              <TrendChart title='Long Term Trend' :data='longdata'/>
              <TrendChart title='Short Term Trend' :data='shortdata'/>
            </div>
            <!-- Stocks Table -->
            <DataTable :items='tickers?.results' keyattr='ticker'>
              <template #headers>
                <th>Ticker</th>
                <th>Name</th>
              </template>
              <template #columns="{item}">
                <td data-title='Ticker'>{{item.ticker}}</td>
                <td data-title='Name'>{{item.info.longName}}</td>
              </template>
            </DataTable>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {onBeforeMount, onMounted, provide, ref, watchEffect} from 'vue'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import {api, utils} from '@/utils'
  import DataTable from '@/components/DataTable.vue'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'
  import StocksSearch from '@/views/stocks/StocksSearch.vue'
  import TrendChart from '@/components/TrendChart.vue'
  
  var stockgroups = {
    'ETFs & Bonds': 'tags:etfs',
    'Nasuni 401k': 'tags:nasuni',
    'Papas Picks': 'tags:dad',
  }

  const tickers = ref(null)
  const shortdata = ref(null)
  const longdata = ref(null)
  const {search} = useUrlParams({search: {type:String}})
  provide('search', {search, updateSearch:(newval) => search.value = newval })

  // On Before Mount
  // Set top navigation
  onBeforeMount(function() { utils.setNavPosition('top') })

  // Watch Search
  // Update the projection trends and stock list
  watchEffect(function() {
    api.Stocks.projectionTrends({periods:'52w,42w,32w,22w,12w', search:search.value})
      .then(resp => longdata.value = resp.data)
      .catch(err => longdata.value = err)
    api.Stocks.projectionTrends({periods:'10w,8w,6w,4w,2w', search:search.value})
      .then(resp => shortdata.value = resp.data)
      .catch(err => shortdata.value = err)
    api.Stocks.getTickers({search:search.value})
      .then(resp => tickers.value = resp.data)
      .catch(err => tickers.value = err)
  })
</script>

<style>
  #stocks {
    .chartlayout {
      display: grid;
      grid-template-rows: 240px;
      grid-template-columns: 100%;
      grid-row-gap: 20px;
      grid-column-gap: 20px;
      margin: 20px 0 20px 0;

      grid-template-columns: calc(50% - 10px) calc(50% - 10px);
      & > div {
        background-color: #00000008;
        border-radius: 6px;
        padding: 15px 10px 10px 10px;
      }
    }
  }
</style>
