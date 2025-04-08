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
              <div v-if='showTocItem(endpt)' class='subitem link' :class='{selected:endpoint==endpt}'
                @click='setPath(endpt.path, endpt.method)'>
                <div class='name'>{{endpt.summary}}</div>
              </div>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <template #content v-if='toc'>
            <ApiSettings/>
            <!-- Request Method, URL and Description -->
            <h1 v-if='endpoint'>{{utils.title(endpoint.category)}} {{endpoint.summary}}</h1>
            <h1 v-else>Unknown Endpoint</h1>
            <div class='inputwrap'>
              <div class='urlwrap'>
                <select v-model='method'><option v-for='meth in allowed' :key='meth' :value='meth'>{{meth}}</option></select>
                <input class='urlinput' type='text' v-model='path' spellcheck='false'
                  @keydown.enter='$event.shiftKey ? sendRequest() : path=$event.target.value'/>
                <Tooltip v-if='axiosSettings.history.value?.length' ref='historyTooltip' class='request-history' position='bottomleft' width='auto' trigger='click'>
                  <template #tooltip>
                    Request History
                    <div class='tablewrap'><table>
                      <tr v-for='(item, i) in axiosSettings.history.value' :key='i' @click.stop='setPath(item.path, item.method, item.data)'>
                        <td>{{item.datetime}}</td>
                        <td>{{item.status}}</td>
                        <td>{{item.method}}</td>
                        <td>{{item.path}}<template v-if='item.data'> - {{item.data}}</template></td>
                        <td>{{item.queries}}</td>
                      </tr>
                    </table></div>
                  </template>
                  <i class='mdi mdi-history' />
                </Tooltip>
              </div>
              <div v-if='method != "GET"' class='paramwrap'>
                <CodeEditor  v-model='params' :showLineNums='true' padding='10px'
                  @keydown.shift.enter.prevent='sendRequest'/>
                <Tooltip class='send-request' position='lefttop'>
                  <template #tooltip>Send Request<div class='subtext'>shift+enter</div></template>
                  <i class='mdi mdi-send' @click='sendRequest'/>
                </Tooltip>
              </div>
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
  import {inject, nextTick, onMounted, ref, watch, watchEffect} from 'vue'
  import {CodeEditor, LayoutPaper, LayoutSidePanel, Tooltip} from '@/components'
  import {ApiSettings} from '@/views/api'
  import {useUrlParams} from '@/composables'
  import {utils} from '@/utils'
  import axios from 'axios'
  
  const APIROOT = '/api/'
  const showheaders = ['content-type', 'content-length', 'response-time', 'queries']
  const axiosSettings = inject('axiosSettings')
  const {method, path} = useUrlParams({method:{}, path:{}})       // Method & path url params
  var toc = ref(null)                                             // Table of contents (api root)
  var endpoint = ref(null)                                        // Current endpoint details
  var historyTooltip = ref(null)                                  // History tooltip
  var params = ref(null)                                          // Current parameters
  var response = ref(null)                                        // Current get response
  const allowed = ref(null)                                       // Allowed methods for current endpoint
  
  // On Mounted
  // Set topnav and fetch toc
  onMounted(async function() {
    utils.setNavPosition('top')
    toc.value = (await axios.get(APIROOT)).data
    if (!path.value || !method.value) {
      var root = toc.value.endpoints.root[0]
      setPath(root.path, root.method)
    }
  })

  // Watch Endpoint
  // Set body params by parsing the description
  watchEffect(function() {
    if (method.value == 'GET') { return }
    if (params.value) { return }
    var docstr = endpoint.value?.description || ''
    var pattern = /•\s*(\w+)\s*\((\w+)\)/g
    var matches = Array.from(docstr.matchAll(pattern))
    var newparams = {}
    for (var [_, name, type] of matches) {
      if (endpoint.value.path.includes(`{${name}}`)) { continue }
      type = type.toLowerCase()
      newparams[name] = type == 'list' ? [] : type == 'dict' ? {} :
        type == 'int' ? 0 : type == 'bool' ? false : ''
    }
    params.value = utils.stringify(newparams, {indent:2})
  })

  // Watch Path
  // Sets the current endpoint and alloed methods
  watchEffect(function() {
    if (!toc.value) { return null }
    const endpoints = Object.values(toc.value.endpoints).flat()
    const matches = endpoints.filter(endpt => pathMatches(path.value, endpt.path))
    allowed.value = matches.length ? matches.map(endpt => endpt.method) : ['GET']
    endpoint.value = matches.find(endpt => endpt.method === method.value) || null
    if (endpoint.value) { method.value = endpoint.value.method }
  })

  // Watch Path
  // Clean messy or incomplete path
  watchEffect(function() {
    if (!toc.value) { return null }
    if (!path.value || !path.value.startsWith(APIROOT)) {
      var root = toc.value.endpoints.root[0]
      setPath(root.path, root.method)
    }
  })

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
        newpath = newpath.replace(axios.defaults.baseURL, '')
        path.value = newpath
        method.value = 'GET'
      })
      span.replaceWith(newspan)
    })
  }

  // Paths Match
  // Check the two paths match
  const pathMatches = function(pstr, tmpl) {
    if (tmpl.includes('/api/')) { tmpl = tmpl.split('/api/')[1] }
    if (pstr.includes('/api/')) { pstr = pstr.split('/api/')[1] }
    if (pstr.includes('?')) { pstr = pstr.split('?')[0] }
    var pattern = tmpl.replace(/{\w+}/g, '[^/]+').replace(/\//g, '\\/')
    return new RegExp(`^${pattern}$`).test(pstr)
  }

  // Set Path
  // Update path and method from the endpoint path
  const setPath = function(newpath, newmethod, newparams) {
    historyTooltip.value?.close()
    method.value = newmethod
    path.value = !newpath.startsWith('http') ? newpath : decodeURIComponent(new URL(newpath).pathname)
    params.value = newparams ? utils.stringify(JSON.parse(newparams), {indent:2}) : null
  }

  // Send Request
  // Send the http request
  const sendRequest = async function() {
    if (path.value === null) { return }
    var payload = (method.value != 'GET') ? JSON.parse(params.value) || {} : undefined
    await axios[method.value.toLowerCase()](path.value, payload)
      .then(resp => response.value = resp)
      .catch(err => response.value = err.response)
    await nextTick()
    linkResponseUrls()
  }

  // Show TOC Item
  // Hide non-get requests if the equivelent get request exists
  const showTocItem = function(endpt) {
    if (endpt.method == 'GET') { return true }
    return !toc.value.endpoints[endpt.category].find(
      e => e.path == endpt.path && e.method == 'GET')
  }

  // Watch Path & Method
  // Check we want to auto send the request
  watch([path, method], function() {
    if (!path.value || !method.value) { return }
    response.value = null
    if (method.value == 'GET' && !path.value.includes('{')) {
      sendRequest()
    }
  }, {immediate:true})
</script>

<style>
  #apidoc {
    /* Header and API Options */
    .description {
      font-size: 14px;
      margin: 20px 0px;
    }

    /* Input Wrap */
    .inputwrap {
      position: relative;
      .urlwrap {
        background-color: #00000008; 
        border-radius: 4px;
        margin-bottom: 10px;
        transition: background-color 0.3s;
        &:has(input:focus) { background-color: #00000010; }
        select {
          background-color: var(--lightbg-bg2);
          border-radius: 4px 0px 0px 4px;
          border-width: 0px;
          box-shadow: none;
          display: inline-block;
          font-family: var(--fontfamily-code);
          font-size: 12px;
          font-weight: bold;
          height: 30px;
          width: 80px;
          &:focus { box-shadow: none; }
        }
        input {
          background-color: transparent;
          border-radius: 0px;
          border-width: 0px;
          box-shadow: none;
          color: var(--lightbg-blue1);
          font-family: var(--fontfamily-code);
          font-size: 12px;
          line-height: 30px;
          padding: 0px 0px 0px 10px;
          width: calc(100% - 90px);
        }
        .request-history {
          position: absolute;
          top: 2px;
          right: 10px;
          font-size: 1.2em;
          .mdi {
            opacity: 0.6;
            cursor: pointer;
            transition: opacity 0.3s ease;
            &:hover { opacity:1; }
          }
          .tablewrap {
            max-height: 300px;
            overflow-y: auto;
            background-color: #1112;
            margin: 5px 0px;
            border-radius: 4px;
            font-size: 11px;
            color: #dcad;
            table {
              border-collapse: collapse;
              border-spacing: 0;
            }
            tr {
              background-color: transparent;
              cursor: pointer;
              transition: all 0.3s ease;
              &:hover { color: var(--darkbg-fg0); background-color: #8885; }
            }
            td {
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              user-select: none;
              padding: 3px 6px;
              max-width: 300px;
            }
          }
        }
      }
      .paramwrap {
        position: relative;
        .codeeditor {
          font-size: 12px;
        }
        .send-request {
          position: absolute;
          bottom: 4px;
          right: 10px;
          z-index: 95;
          .mdi {
            opacity: 0.6;
            cursor: pointer;
            transition: opacity 0.3s ease;
            &:hover { opacity:1; }
          }
        }
      }
    }

    /* API Response */
    .headers {
      font-size: 12px;
      margin: 5px 0px 20px 0px;
      font-family: var(--fontfamily-code);
      .label { font-weight:bold; margin-right:5px; }
      .value { color:var(--lightbg-blue1) }
    }
    pre, code {
      font-size: 11px;
      line-height: 1.3;
      .link {
        cursor: pointer;
        transition: color 0.3s;
        &:hover { color:var(--fgcolor); }
      }
    }
  }
</style>

