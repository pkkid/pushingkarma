<template>
  <div id='apidoc'>
    <LayoutSidePanel width='250px'>
      <!-- Side Panel: API Categorties -->
      <template #panel>
        <div v-if='toc' class='menu'>
          <template v-for='[category, endpts] in Object.entries(toc.endpoints)' :key='category'>
            <div class='item'>
              <i class='mdi' :class='getIcon(category)'/>
              {{utils.title(category)}}
            </div>
            <template v-for='endpt in endpts' :key='`${endpt.method} ${endpt.path}`'>
              <div class='subitem link' :class='{selected:endpoint===endpt}' @click='setPath(endpt)'>
                <div class='name'>{{endpt.summary}}</div>
              </div>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <template #content v-if='toc'>
            <!-- Request Options: Count Queries and Log Queries -->
            <div class='options'>
              <Tooltip width='250px' text='An additonal Queries header is added to api requests
                detailing the count and duration of sql queries.'>
                <ToggleSwitch :value='countQueries' label='Count Queries' @update='setCountQueries'/>
              </Tooltip>
              <Tooltip width='250px' text='Enables server side logging of all sql queries and their duration.'>
                <ToggleSwitch :value='logQueries' label='Log Queries' @update='setLogQueries'/>
              </Tooltip>
            </div>
            <!-- Request Method, URL and Description -->
            <h1>{{endpointName}}</h1>
            <div class='inputwrap'>
              <select v-model='method'>
                <option v-for='meth in allowed' :key='meth' :value='meth'>{{meth}}</option>
              </select>
              <input class='urlinput' type='text' :value='path' spellcheck='false' @keydown.enter='path=$event.target.value'/>
            </div>
            <div class='description' v-html='endpoint?.description.replace(/\n/g, "<br/>")'></div>
            <!-- Response Headers and Content -->
            <template v-if='response'>
              <div class='headers'>
                <span class='label'>HTTP {{response.status}} {{response.statusText}}</span><br/>
                <template v-for='header in showheaders'>
                  <div v-if='response.headers[header]' :key='header'>
                    <span class='label'>{{utils.title(header)}}:</span>
                    <span class='value'>{{response.headers[header]}}</span><br/>
                  </div>
                </template>
              </div>
              <div theme='gruvbox-light-hard' class='codearea'>
                <highlightjs :code='utils.stringify(response?.data || "", {indent:2})' language='json' :autodetect='false'/>
              </div>
            </template>
            <div v-else class='headers'>
              <span class='label'>{{method}} request not initiated</span>
            </div>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {computed, inject, nextTick, onBeforeMount, onMounted, ref, watch, watchEffect} from 'vue'
  import {LayoutPaper, LayoutSidePanel} from '@/components/Layout'
  import {ToggleSwitch, Tooltip} from '@/components'
  import {useUrlParams} from '@/composables'
  import {utils} from '@/utils'
  import axios from 'axios'
  
  var APIROOT = '/api/'
  var showheaders = ['allow', 'content-type', 'content-length', 'response-time', 'queries']
  const {countQueries, setCountQueries} = inject('countQueries')  // Count queries on the server
  const {logQueries, setLogQueries} = inject('logQueries')        // Log queries on the server
  const {method, path} = useUrlParams({
    method: {type:String},                        // Current method to display
    path: {type:String}                           // Current path to display
  })
  var toc = ref(null)                             // Table of contents (api root)
  var endpoint = ref(null)                        // Current endpoint details
  var response = ref(null)                        // Current get response
  const allowed = ref(null)                       // Allowed methods for current endpoint

  // Endpoint Name
  // Return the endpoint name from the path
  const endpointName = computed(function() {
    if (!endpoint.value) { return 'Unknown Endpoint' }
    return `${utils.title(endpoint.value.category)} ${endpoint.value.summary}`
  })

  // On Mounted
  // Set topnav and fetch toc
  onMounted(async function() {
    utils.setNavPosition('top')
    toc.value = (await axios.get(APIROOT)).data
    if (!path.value || !method.value) {
      setPath(toc.value.endpoints.root[0])
    }
  })

  // Watch Path
  // Sets the current endpoint and alloed methods
  watchEffect(function() {
    if (!toc.value) { return null }
    var allow = []
    for (const [category, endpts] of Object.entries(toc.value.endpoints)) {
      for (const endpt of endpts) {
        if (pathMatches(path.value, endpt.path)) {
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

  // Watch Path
  // Clean messy or incomplete path
  watchEffect(function() {
    if (!toc.value) { return null }
    if (!path.value || !path.value.startsWith(APIROOT)) {
      setPath(toc.value.endpoints.root[0])
    }
  })

  // Watch Path & Method
  // Check we want to auto send the request
  watch([path, method], function() {
    if (!toc.value || !path.value || !method.value) { return }
    response.value = null
    if (method.value == 'GET') { sendRequest() }
  }, {immediate:true})

  // Get Icon
  // Icon for the API Category
  const getIcon = function(category) {
    switch (category) {
      case 'budget': return 'mdi-piggy-bank-outline'
      case 'main': return 'mdi-earth'
      case 'obsidian': return 'mdi-notebook-outline'
      case 'stocks': return 'mdi-chart-line'
      default: return 'mdi-code-braces'
    }
  }

  // Link Response URLs
  // Create links in highlight.js output
  const linkResponseUrls = function() {
    var spans = document.querySelectorAll('.codearea pre code span.hljs-string')
    spans = Array.from(spans).filter(span => span.textContent.startsWith(`"${axios.defaults.baseURL}`))
    spans.forEach(span => {
      const newspan = document.createElement('span')
      newspan.textContent = span.textContent
      newspan.style.cursor = 'pointer'
      newspan.className = `${span.className} link`
      newspan.addEventListener('click', () => {
        var newpath = newspan.textContent.slice(1, -1)
        newpath = '/api/' + newpath.replace(axios.defaults.baseURL, '')
        path.value = newpath
        method.value = 'GET'
      })
      span.replaceWith(newspan)
    })
  }

  // Paths Match
  // Check the two paths match
  const pathMatches = function(tmpl, pstr) {
    if (tmpl.includes('/api/')) { tmpl = tmpl.split('/api/')[1] }
    if (pstr.includes('/api/')) { pstr = pstr.split('/api/')[1] }
    var pattern = pstr.replace(/{\w+}/g, '[^/]+').replace(/\//g, '\\/')
    return new RegExp(`^${pattern}$`).test(tmpl)
  }

  // Set Path
  // Update path and method from the endpoint path
  const setPath = function(endpt) {
    path.value = new URL(endpt.path).pathname
    method.value = endpt.method
  }

  // Send Request
  // Send the http request
  const sendRequest = async function() {
    if (path.value === null) { return }
    await axios[method.value.toLowerCase()](path.value)
      .then(resp => response.value = resp)
      .catch(err => response.value = err.response)
    await nextTick()
    linkResponseUrls()
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

