<template>
  <div id='apidoc'>
    <LayoutSidePanel>
      <!-- API Categorties -->
      <template #panel>
        <div class='menu'>
          <template v-for='category in catergories' :key='category'>
            <div class='item'>
              <span class='icon'>{{categoryIcon(category)}}</span>
              {{utils.title(category)}}
            </div>
            <template v-for='item in categoryItems(category)' :key='`${category}/${item}`'>
              <div class='subitem link' @click="view=`${category}/${item}`">
                <div class='name'>{{utils.title(item)}}</div>
              </div>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <!-- Note Content-->
          <template #content>
            <h1>API Root</h1>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {computed, onBeforeMount, ref} from 'vue'
  import {utils} from '@/utils'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import axios from 'axios'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'

  var toc = ref(null)
  const {view} = useUrlParams({
    view: {type:String},
  })

  onBeforeMount(async function() {
    utils.setNavPosition('top')
    var data = await axios.get('')
    toc.value = data.data
  })

  // Categories
  // List of API Categories
  const catergories = computed(function() {
    if (toc.value == null) { return [] }
    var categories = []
    Object.keys(toc.value).forEach(key => {
      var category = key.split('/')[0]
      if (!categories.includes(category)) {
        categories.push(category)
      }
    })
    return categories
  })

  // Cateogry Items
  // List of API Items for the Category
  const categoryItems = function(category) {
    if (toc.value == null) { return [] }
    var items = []
    Object.keys(toc.value).forEach(key => {
      if (key.startsWith(category)) {
        items.push(key.split('/')[1])
      }
    })
    return items
  }

  // Category Icon
  // Icon for the API Category
  const categoryIcon = function(category) {
    switch (category) {
      case 'budget': return 'savings'
      case 'main': return 'public'
      case 'obsidian': return 'description'
      case 'stocks': return 'monitoring'
      default: return 'code'
    }
  }
</script>
