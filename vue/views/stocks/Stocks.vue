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
                <th><div class='thwrap ticker'>Ticker</div></th>
                <th><div class='thwrap name'>Name</div></th>
                <th><div class='thwrap close'>Close</div></th>
                <th><div class='thwrap change200d'>200-Day</div></th>
                <th><div class='thwrap change50d'>50-Day</div></th>
                <th><div class='thwrap beta'>Beta</div></th>
              </template>
              <template #columns="{item}">
                <!-- Ticker -->
                <td><div class='tdwrap ticker'>
                  {{item.ticker}}
                </div></td>
                <!-- Name & Category -->
                <td><div class='tdwrap name'>
                  <div>
                    {{item.info.longName}}
                    <div class='subtext'>
                      {{utils.title(item.info.category || item.info.industry || item.info.quoteType.toLowerCase())}}
                    </div>
                  </div>
                </div></td>
                <!-- Close -->
                <td><div class='tdwrap close'>
                  {{utils.usd(item.lastday.close)}}
                </div></td>
                <!-- Close 200-Day -->
                <td><div class='tdwrap change200d'>
                  {{utils.round(item.info.twoHundredDayAverageChange, 2)}}%
                </div></td>
                <!-- Close 50-Day -->
                <td><div class='tdwrap change50d'>
                  {{utils.round(item.info.fiftyDayAverageChange, 2)}}%
                </div></td>
                <!-- Beta -->
                <td><div class='tdwrap change50d'>
                  {{item.info.beta || item.info.beta3Year}}
                </div></td>
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
      .thwrap, .tdwrap { display:flex; align-items:center; justify-content: center; }
      .thwrap { font-size:10px; line-height: 1.3;  height:20px;}
      .name { flex-direction: row; justify-content: flex-start; }
    }

    .subtext {
      font-size: 0.7em;
      opacity: 0.6;
      margin-top: -2px;
    }

  }
</style>
