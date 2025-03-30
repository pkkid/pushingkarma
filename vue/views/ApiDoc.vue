<template>
  <div id='apidoc'>
    <LayoutSidePanel width='250px'>
      <!-- API Categorties -->
      <template #panel>
        <div v-if='toc' class='menu'>
          <template v-for='[category, endpts] in Object.entries(toc.endpoints)' :key='category'>
            <template v-if='category.length'>
              <div class='item'>
                <i class='mdi' :class='categoryIcon(category)'/>
                {{utils.title(category)}}
              </div>
              <template v-for='endpt in endpts' :key='`${endpt.method} ${endpt.path}`'>
                <!-- {{console.log(endpoint===endpt, 'endpoint', endpoint, 'endpt', endpt)}} -->
                <div class='subitem link' :class='{selected:endpoint===endpt}' @click='setView(endpt)'>
                  <div class='name'>{{endpt.summary}}</div>
                </div>
              </template>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <template #content v-if='toc && response'>
            <div class='options'>
              <!-- Count Queries -->
              <Tooltip width='250px' text='An additonal Queries header is added to api requests
                detailing the count and duration of sql queries.'>
                <ToggleSwitch :value='countQueries' label='Count Queries' @update='setCountQueries'/>
              </Tooltip>
              <!-- Log Queries -->
              <Tooltip width='250px' text='Enables server side logging of all sql queries and their duration.'>
                <ToggleSwitch :value='logQueries' label='Log Queries' @update='setLogQueries'/>
              </Tooltip>
            </div>
            <!-- Request Description and URL -->
            <h1>{{endpointName}}</h1>
            <!-- Input Wrap -->
            <div class='inputwrap'>
              <select v-model='method'>
                <option v-for='meth in allowed' :key='meth' :value='meth'>{{meth}}</option>
              </select>
              <input class='urlinput' type='text' :value='view' spellcheck='false' @keydown.enter='view=$event.target.value'/>
            </div>
            <div class='description' v-html='endpoint?.description.replace(/\n/g, "<br/>")'></div>
            <div class='headers'>
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
            <div theme='gruvbox-light-hard' class='codearea'>
              <highlightjs :code='utils.stringify(response.data, {indent:2})' language='json' :autodetect='false'/>
            </div>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {computed, inject, nextTick, onBeforeMount, ref, watch, watchEffect} from 'vue'
  import {LayoutPaper, LayoutSidePanel} from '@/components/Layout'
  import {ToggleSwitch, Tooltip} from '@/components'
  import {useUrlParams} from '@/composables'
  import {utils} from '@/utils'
  import axios from 'axios'
  
  // Icon for each API cateogry
  var categoryIcons = {
    'budget': 'mdi-piggy-bank-outline',
    'main': 'mdi-earth',
    'obsidian': 'mdi-notebook-outline',
    'stocks': 'mdi-chart-line',
    'default': 'code',
  }
  
  var showheaders = ['allow', 'content-type', 'content-length', 'response-time', 'queries']
  // const countQueries = useStorage('axios.countqueries', false)  
  // const logQueries = useStorage('axios.logqueries', false)      // Log queries on the server
  
  const {countQueries, setCountQueries} = inject('countQueries')  // Count queries on the server
  const {logQueries, setLogQueries} = inject('logQueries')        // Log queries on the server
  const {method, view} = useUrlParams({
    method: {type:String},                        // Current method to display
    view: {type:String}                           // Current view to display
  })
  var toc = ref(null)                             // Table of contents (api root)
  var endpoint = ref(null)                        // Current endpoint details
  var response = ref(null)                        // Current get response
  const allowed = ref(null)                       // Allowed methods for current endpoint

  // Endpoint Name
  // Return the endpoint name from the view
  const endpointName = computed(function() {
    if (!endpoint.value) { return 'Unknown Endpoint' }
    return `${utils.title(endpoint.value.category)} ${endpoint.value.summary}`
  })

  // Endpoint View
  // Return the endpoint details from the view
  watchEffect(function() {
    if (!toc.value) { return null }
    var allow = []
    for (const [category, endpts] of Object.entries(toc.value.endpoints)) {
      for (const endpt of endpts) {
        if (pathMatches(view.value, endpt.path)) {
          allow.push(endpt.method)
          if (endpt.method == method.value) {
            endpt.category = category
            endpoint.value = endpt
            method.value = endpt.method
          }
        }
      }
    }
    allowed.value = allow.length ? allow : ['GET']
  })

  // On Before Mount
  // Update to top nav and get the toc
  onBeforeMount(async function() {
    utils.setNavPosition('top')
    method.value = method.value || 'GET'
    toc.value = (await axios.get('')).data
  })

  // Watch View
  // Clean messy view strings
  watchEffect(function() {
    if (view.value == null) { view.value = '/api/' }
    else if (view.value.length <= 5) { view.value = '/api/' }
    else if (!view.value.startsWith('/api/')) {
      view.value = `/api/${view.value}`.replace(/\/\//g, '/')
    }
  })

  // Get View
  // Returns view name from the endpoint path
  const setView = function(endpoint) {
    view.value = `/api/${endpoint.path.split('/api/')[1]}`
    method.value = endpoint.method
  }

  // Category Icon
  // Icon for the API Category
  const categoryIcon = function(category) {
    return categoryIcons[category] || categoryIcons['default']
  }

  // Watch View
  // Auto send request method=GET
  watchEffect(async function() {
    if (view.value === null) { return }
    if (method.value == 'GET') { sendRequest() }
  })

  // Send Request
  // Send the http request!
  const sendRequest = async function() {
    if (view.value === null) { return }
    var endpoint = view.value.replace(/\/api\//g, '')
    await axios[method.value.toLowerCase()](endpoint)
      .then(resp => response.value = resp)
      .catch(err => response.value = err.response)
    await nextTick()
    linkAPIURLs()
  }

  // Link API URLs
  // Create links for all api urls
  const linkAPIURLs = function() {
    var spans = document.querySelectorAll('.codearea pre code span.hljs-string')
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

  // Paths Match
  // Check the two paths match
  const pathMatches = function(tmpl, path) {
    if (tmpl.includes('/api/')) { tmpl = tmpl.split('/api/')[1] }
    if (path.includes('/api/')) { path = path.split('/api/')[1] }
    var pattern = path.replace(/{\w+}/g, '[^/]+').replace(/\//g, '\\/')
    return new RegExp(`^${pattern}$`).test(tmpl)
  }
</script>

<style>
  #apidoc {
    .description {
      font-size: 14px;
      margin: 20px 0px;
    }
    .options {
      float: right;
      display: flex;
      flex-direction: column;
      font-size: 10px;
      gap: 3px;
    }
    .inputwrap {
      background-color: #00000008; 
      border-radius: 4px;
      margin: -10px 0px 20px -2px;
      transition: background-color 0.3s;
      &:has(input:focus) { background-color: #00000010; }
      select {
        background-color: #00000008;
        background-color: var(--lightbg-bg2);
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 0px;
        border-top-left-radius: 4px;
        border-top-right-radius: 0px;
        border-width: 0px;
        display: inline-block;
        font-family: var(--fontfamily-code);
        font-size: 12px;
        font-weight: bold;
        height: 30px;
        padding: 2px 3px;
        width: 80px;
      }
      input {
        background-color: transparent;
        border-width: 0px;
        border-radius: 0px;
        box-shadow: none;
        color: var(--lightbg-blue1);
        font-family: var(--fontfamily-code);
        font-size: 12px;
        padding: 0px 0px 0px 10px;
        line-height: 30px;
        width: calc(100% - 90px);
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

