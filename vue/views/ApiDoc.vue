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
              <div class='subitem link' @click="view=`/api/${category}/${item}`">
                <div class='name'>{{utils.title(item)}}</div>
              </div>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <!-- Note Content-->
          <template #content v-if='options && response'>
            <h1>{{viewName}}</h1>
            <div class='description' v-html='options.data?.description?.replace(/\n/g, "<br/>")'></div>
            <div class='headers'>
              <div class='inputwrap'>
                <span class='label'>GET</span>
                <input class='urlinput' type='text' v-model='url' spellcheck='false' @keydown.enter='view=url'/>
              </div>
              <span class='label'>HTTP {{response.status}} {{response.statusText}}</span><br/>
              <span class='label'>Allow:</span><span class='value'>{{options.headers.allow}}</span><br/>
              <span class='label'>Content-Type:</span><span class='value'>{{response.headers['content-type']}}</span><br/>
              <span class='label'>Content-Length:</span><span class='value'>{{response.headers['content-length']}}</span><br/>
            </div>
            <div class='code-block'>
              <highlightjs :code='utils.stringify(response.data, {indent:2})' :language='"json"' :autodetect='false'/>
            </div>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {computed, nextTick, onBeforeMount, ref, watch, watchEffect} from 'vue'
  import {utils} from '@/utils'
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import axios from 'axios'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'

  var toc = ref(null)         // Table of contents (api root)
  var options = ref(null)     // Current options response
  var response = ref(null)    // Current get response
  const {view} = useUrlParams({view: {type:String}})
  const url = ref(view.value)

  // Watch View
  // Keep the url updated when view changed
  watch(view, (newValue) => { url.value = newValue})

  // On Before Mount
  // Update to top nav and get the toc
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

  // View Name
  // Return the current view title
  const viewName = computed(function() {
    if (view.value == null) { return 'PushingKarma API' }
    var endpoint = view.value.replace(/\/api\//g, '')
    endpoint = endpoint.split('?')[0]
    return utils.title(endpoint.replace(/\//g, ' '))
  })

  // View Options
  // Return the current view options
  watchEffect(async function() {
    if (view.value == null) { return {} }
    var endpoint = view.value.replace(/\/api\//g, '')
    await axios.options(endpoint)
      .then(resp => options.value = resp)
      .catch(err => options.value = err.response)
    await axios.get(endpoint)
      .then(resp => response.value = resp)
      .catch(err => response.value = err.response)
    console.debug(`${endpoint} options`, options.value)
    console.debug(`${endpoint} response`, response.value)
    nextTick(linkAPIURLs)
  })

  // Link API URLs
  // Create links for all api urls
  const linkAPIURLs = function() {
    var spans = document.querySelectorAll('.code-block pre code span.hljs-string')
    spans = Array.from(spans).filter(span => span.textContent.startsWith(`"${axios.defaults.baseURL}`))
    spans.forEach(span => {
      const newspan = document.createElement('span')
      newspan.textContent = span.textContent
      newspan.style.cursor = 'pointer'
      newspan.className = `${span.className} link`
      newspan.addEventListener('click', () => {
        var newview = newspan.textContent.slice(1, -1)
        newview = '/api/' + newview.replace(axios.defaults.baseURL, '')
        view.value = newview
      })
      span.replaceWith(newspan)
    })
  }
</script>

<style>
  #apidoc {
    .description {
      font-size: 14px;
      margin-top: -10px;
    }
    .inputwrap {
      background-color: transparent;
      border-radius: 4px;
      margin-left: -8px;
      padding-left: 8px;
      margin-bottom: 5px;
      transition: background-color 0.3s;
      &:has(input:focus) { background-color: #00000008; }
      input {
        background-color: transparent;
        border-width: 0px;
        box-shadow: none;
        color: var(--lightbg-blue1);
        font-family: var(--fontfamily-code);
        font-size: 12px;
        padding: 8px 0px;
        width: calc(100% - 30px);
      }
    }
    .headers {
      font-size: 12px;
      margin: 5px 0px 20px 0px;
      font-family: var(--fontfamily-code);
      .label { font-weight:bold; margin-right:5px; }
      .value { color:var(--lightbg-blue1) }
    }
    pre, code {
      font-size:11px;
      line-height:1.3;
      .link {
        cursor: pointer;
        transition: color 0.3s;
        &:hover { color: var(--fgcolor); }
      }
    }
  }
</style>

