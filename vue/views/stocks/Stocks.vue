<template>
  <div id='stocks'>
    <LayoutPaper id='budgetsettings' width='1000px'>
      <template #content>
        <h1>Stocks</h1>
        <div class='chartlayout' style='margin-top:20px;'>
          <TrendChart title='Long Term Trend' :data='longdata'/>
          <TrendChart title='Short Term Trend' :data='shortdata'/>
        </div>
      </template>
    </LayoutPaper>
  </div>
</template>

<script setup>
  import {onBeforeMount, onMounted, ref} from 'vue'
  import {utils} from '@/utils'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import TrendChart from '@/components/TrendChart.vue'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import {api} from '@/utils'

  const shortdata = ref(null)
  const longdata = ref(null)

  onBeforeMount(function() { utils.setNavPosition('top') })

  onMounted(function() {
    api.Stocks.projectionTrends({periods:'52w,42w,32w,22w,12w', search:'tags:etfs'})
      .then(resp => longdata.value = resp.data)
      .catch(err => longdata.value = err)
    api.Stocks.projectionTrends({periods:'10w,8w,6w,4w,2w', search:'tags:etfs'})
      .then(resp => shortdata.value = resp.data)
      .catch(err => shortdata.value = err)
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
        padding: 10px;
      }
    }
  }
</style>
