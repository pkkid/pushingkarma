<template>
  <div id='apidoc'>
    <LayoutSidePanel width='250px'>
      <!-- API Categorties -->
      <template #panel>
        <div class='menu'>
          <template v-for='category in catergories' :key='category'>
            <div class='item'>
              <i class='mdi' :class='categoryIcon(category)'/>
              {{utils.title(category)}}
            </div>
            <template v-for='item in categoryItems(category)' :key='`${category}/${item}`'>
              <div class='subitem link' :class='{selected:view === `/api/${category}/${item}`}' 
                @click='view=`/api/${category}/${item}`'>
                <div class='name'>{{utils.title(item)}}</div>
              </div>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <template #content v-if='options && response'>
            <div class='options'>
              <!-- Count Queries -->
              <Tooltip width='250px' text="An additonal 'Queries' header is added to api requests
                detailing the count and duration of sql queries.">
                <ToggleSwitch v-model="countQueries" label="Count Queries" @update='toggleCountQueries'/>
              </Tooltip>
              <!-- Log Queries -->
              <Tooltip width='250px' text="Enables server side logging of all sql queries and their duration.">
                <ToggleSwitch v-model="logQueries" label="Log Queries" @update='toggleLogQueries'/>
              </Tooltip>
            </div>
            <!-- Request Description and URL -->
            <h1>{{viewName}}</h1>
            <div class='description' v-html='options.data?.description?.replace(/\n/g, "<br/>")'></div>
            <div class='headers'>
              <div class='inputwrap'>
                <span class='label'>GET</span>
                <input class='urlinput' type='text' v-model='url' spellcheck='false' @keydown.enter='view=url'/>
              </div>
              <!-- Response Headers -->
              <span class='label'>HTTP {{response.status}} {{response.statusText}}</span><br/>
              <template v-for='header in showheaders'>
                <div v-if='response.headers[header]' :key='header'>
                  <span class='label'>{{utils.title(header)}}:</span>
                  <span class='value'>{{response.headers[header]}}</span><br/>
                </div>
              </template>
            </div>
            <!-- Response Content -->
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
  import {useUrlParams} from '@/composables/useUrlParams.js'
  import {useStorage} from '@/composables/useStorage'
  import {utils} from '@/utils'
  import axios from 'axios'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'
  import ToggleSwitch from '@/components/ToggleSwitch.vue'
  import Tooltip from '@/components/Tooltip.vue'
  // Icon for each API cateogry
  var categoryIcons = {
    'budget': 'mdi-piggy-bank-outline',
    'main': 'mdi-earth',
    'obsidian': 'mdi-notebook-outline',
    'stocks': 'mdi-chart-line',
    'default': 'code',
  }
  var showheaders = ['allow', 'content-type', 'content-length', 'response-time', 'queries']
  var toc = ref(null)         // Table of contents (api root)
  var options = ref(null)     // Current options response
  var response = ref(null)    // Current get response
  
  const countQueries = useStorage('axios.countqueries', false)  // Count queries on the server
  const logQueries = useStorage('axios.logqueries', false)      // Log queries on the server
  const {view} = useUrlParams({view: {type:String}})            // Current view to display
  const url = ref(view.value)                                   // Current url to display

  // Watch View
  // Keep the url updated when view changed
  watch(view, function(newval) {
    checkView()
    url.value = newval
  })

  // On Before Mount
  // Update to top nav and get the toc
  onBeforeMount(async function() {
    utils.setNavPosition('top')
    toggleCountQueries(countQueries.value)
    toggleLogQueries(logQueries.value)
    checkView()
    toc.value = (await axios.get('')).data
  })

  // Check View
  // Make sure view is not null and starts with /api/
  const checkView = function() {
    if (view.value == null) {
      view.value = '/api/'
    } else if (!view.value.startsWith('/api/')) {
      view.value = `/api/${view.value}`.replace(/\/\//g, '/')
    }
  }

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
    return categoryIcons[category] || categoryIcons['default']
  }

  // View Name
  // Return the current view title
  const viewName = computed(function() {
    if (view.value == '/api/') { return 'PushingKarma API' }
    var endpoint = view.value.replace(/\/api\//g, '')
    endpoint = endpoint.split('?')[0]
    return utils.title(endpoint.replace(/\//g, ' '))
  })

  // View Options
  // Return the current view options
  watchEffect(async function() {
    if (view.value === null) { return }
    var endpoint = view.value.replace(/\/api\//g, '')
    await Promise.all([
      axios.options(endpoint)
        .then(resp => options.value = resp)
        .catch(err => options.value = err.response),
      axios.get(endpoint)
        .then(resp => response.value = resp)
        .catch(err => response.value = err.response)
   ])
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

  // Toggle Count Queries
  // Includes the Count-Queries header in requests
  const toggleCountQueries = function(newval) {
    countQueries.value = newval
    if (newval) { axios.defaults.headers.common['Count-Queries'] = 'true' }
    else { delete axios.defaults.headers.common['Count-Queries'] }
  }
  
  // Toggle Log Queries
  // Includes the Log-Queries header in requests
  const toggleLogQueries = function(newval) {
    logQueries.value = newval
    if (newval) { axios.defaults.headers.common['Log-Queries'] = 'true' }
    else { delete axios.defaults.headers.common['Log-Queries'] }
  }
</script>

<style>
  #apidoc {
    .description {
      font-size: 14px;
      margin-top: -10px;
    }
    .options {
      float: right;
      display: flex;
      flex-direction: column;
      font-size: 10px;
      gap: 3px;
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

