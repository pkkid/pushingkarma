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
            <h1>Stock Analysis</h1>
            <div class='chartlayout' style='margin-top:20px;'>
              <TrendChart title='Long Term Trend' :data='longdata'/>
              <TrendChart title='Short Term Trend' :data='shortdata'/>
            </div>
            <!-- Stocks Table -->
            <DataTable :items='tickers?.results' keyattr='ticker'>
              <template #columns="{item}">
                <!-- Ticker -->
                <Column title='Ticker'>
                  {{item.ticker}}
                </Column>
                <!-- Name -->
                <Column title='Name'>
                  {{item.info.longName}}
                  <div class='subtext'>
                    {{utils.title(item.info.category || item.info.industry || item.info.quoteType.toLowerCase())}}
                  </div>
                </Column>
                <!-- Close -->
                <Column title='Close'>
                  {{utils.usd(item.lastday.close)}}
                </Column>
                <!-- Change 200d -->
                <Column title='Change 200d'>
                  {{utils.round(item.info.twoHundredDayAverageChange, 2)}}%
                </Column>
                <!-- Change 50d -->
                <Column title='Change 25d'>
                  {{utils.round(item.info.fiftyDayAverageChange, 2)}}%
                </Column>
                <!-- Beta -->
                <Column title='Beta'>
                  {{item.info.beta || item.info.beta3Year}}
                </Column>
              </template>
            </DataTable>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {onBeforeMount, provide, ref, watchEffect} from 'vue'
  import {LayoutPaper, LayoutSidePanel} from '@/components/Layout'
  import {DataTable, DataTableColumn as Column} from '@/components/DataTable'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import {api, utils} from '@/utils'
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
      grid-column-gap: 20px;
      grid-row-gap: 20px;
      grid-template-columns: 100%;
      grid-template-columns: calc(50% - 10px) calc(50% - 10px);
      grid-template-rows: 240px;
      margin: 20px 0 20px 0;
      & > div {
        background-color: #eaeae7;
        border-radius: 6px;
        padding: 15px 10px 10px 10px;
      }
    }
    .datatable {
      .thwrap, .tdwrap { line-height:1.3; padding:5px 10px; text-align:center;}
      .thwrap { font-size:10px; }
      tr [data-name='name'] > div { text-align:left; }
    }
  }
</style>
