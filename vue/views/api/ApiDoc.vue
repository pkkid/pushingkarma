<template>
  <div id='apidoc'>
    <LayoutSidePanel width='250px'>
      <!-- Side Panel: API Categorties -->
      <template #panel>
        <div v-if='toc' class='menu'>
          <template v-for='[category, endpts] in Object.entries(categories)' :key='category'>
            <div class='item'>
              <i class='mdi' :class='ICONS[category] || "mdi-code-braces"'/>
              {{utils.title(category)}}
            </div>
            <template v-for='endpt in endpts' :key='endpt.path'>
              <div class='subitem link' :class='{selected: endpt.path==endpoint?.path}'
                @click='setupRequest(endpt.path, endpt.method)'>
                <div class='name'>{{endpt.summary}}</div>
              </div>
            </template>
          </template>
        </div>
      </template>
      <template #content>
        <LayoutPaper>
          <template #content >
            <div v-if='toc'>
              <ApiSettings/>
              <!-- Request Method, URL and Description -->
              <h1 v-if='endpoint'>{{utils.title(endpoint.category)}} {{endpoint.summary}}</h1>
              <h1 v-else>Unknown Endpoint</h1>
              <div class='inputwrap'>
                <div class='urlwrap'>
                  <select v-model='method'>
                    <option v-for='meth in allowed' :key='meth' :value='meth'>{{meth.toUpperCase()}}</option>
                  </select>
                  <input class='urlinput' type='text' v-model='_path' spellcheck='false'
                    @change='setupRequest(_path, method.value, null, false)'
                    @keydown.enter.stop='sendRequest'/>
                  <!-- History Tooltip -->
                  <Tooltip v-if='axiosSettings.history.value?.length' ref='historyTooltip'
                    class='request-history' position='bottomleft' width='auto' trigger='click'>
                    <template #tooltip>
                      Request History
                      <div class='tablewrap'><table>
                        <tr v-for='(item, i) in axiosSettings.history.value' :key='i'
                          @click.stop='setupRequest(item.path, item.method, item.data)'>
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
                <!-- Content Body -->
                <div v-if='showPayload' class='payloadwrap'>
                  <CodeEditor v-model='payload' :showlinenums='true' padding='10px' @keydown.shift.enter.prevent='sendRequest'/>
                  <Tooltip class='send-request' position='lefttop'>
                    <template #tooltip>Send Request<div class='subtext'>shift+enter</div></template>
                    <i class='mdi mdi-send' @click='sendRequest'/>
                  </Tooltip>
                </div>
              </div>
              <!-- Endpoint Description & Parameters -->
              <div class='description'>
                <div v-html='endpoint?.description'/>
                <ul style='font-size:1em;'>
                  <li v-for='param in params' :key='param.name'>
                    {{param.name}} ({{param.in}} {{param.type}}): {{param.description}}
                  </li>
                </ul>
              </div>
              <!-- Response Headers and Content -->
              <template v-if='response'>
                <div class='headers'>
                  <span class='label'>HTTP {{response.status}} {{response.statusText}}</span><br/>
                  <template v-for='header in HEADERS' :key='header'>
                    <div v-if='response.headers[header]'>
                      <span class='label'>{{utils.title(header)}}:</span>
                      <span class='value'>{{response.headers[header]}}</span><br/>
                    </div>
                  </template>
                </div>
                <CodeEditor :value='content' showlinenums language='json' readonly/>
              </template>
              <!-- No Response and Loading -->
              <template v-else>
                <div class='headers'>
                  <span class='label'>HTTP {{method.toUpperCase()}} Request Not Initiated</span>
                </div>
                <IconMessage v-if='loading' height='200px' icon='pk' animation='gelatine'
                  text='Fetching Response' ellipsis style='background-color:#ddddd9;'/>
              </template>
            </div>
            <IconMessage v-else icon='pk' animation='gelatine' text='Loading API root' ellipsis/>
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {computed, inject, nextTick, onMounted, ref, watch} from 'vue'
  import {CodeEditor, IconMessage, LayoutPaper, LayoutSidePanel, Tooltip} from '@/components'
  import {ApiSettings} from '@/views/api'
  import {useUrlParams} from '@/composables'
  import {utils} from '@/utils'
  import axios from 'axios'
  
  const APIROOT = '/api/'
  const ICONS = {'budget':'mdi-piggy-bank-outline', 'main':'mdi-earth',
    'obsidian':'mdi-notebook-outline', 'stocks':'mdi-chart-line'}
  const HEADERS = ['content-length', 'content-type', 'queries', 'response-time']

  const axiosSettings = inject('axiosSettings')
  const {method, path} = useUrlParams({method:{}, path:{}})  // Method & path url params
  var allowed = ref(null)                 // Allowed methods for current endpoint
  var endpoint = ref(null)                // Current endpoint details
  var historyTooltip = ref(null)          // History tooltip
  var loading = ref(false)                // True when loading a request
  var payload = ref(null)                 // Current body payload
  var response = ref(null)                // Current get response
  var toc = ref(null)                     // Table of contents (api root)
  var _path = ref(null)                   // Current input value

  var content = computed(() => utils.stringify(response.value?.data || "", {indent:2, maxlen:100}))

  // Categories
  // Computes object of {category: [endpoints]} to display in the sidepanel
  const categories = computed(function() {
    if (!toc.value) { return [] }
    var result = {}
    for (const [epath, endpts] of Object.entries(toc.value.paths)) {
      var category = epath.replace('/api/', '').split('/')[0] || 'root'
      if (!(category in result)) { result[category]  = [] }
      for (const [emethod, details] of Object.entries(endpts)) {
        if ((category == 'root' && epath == APIROOT) || epath.startsWith(`${APIROOT}${category}/`)) {
          result[category].push({...details, path:epath, method:emethod, category:category})
          break
        }
      }
    }
    return result
  })

  // Show Payload
  // True if we want to show the payload editor
  const showPayload = computed(function() {
    if (method.value == 'get') { return false }
    if (endpoint.value?.requestBody?.content['multipart/form-data']) { return false }
    return true
  })

  // Params
  // Computes paramaters for the current endpoint
  const params = computed(function() {
    if (!endpoint.value) { return [] }
    var result = []
    // Iterate the path and query parameters
    for (var param of Object.values(endpoint.value.parameters)) {
      result.push({name:param.name, type:param.schema.type, in:param.in,
        required:param.required, description:param.schema.description})
    }
    // Iterate the contentBody schema parameters
    if (endpoint.value.requestBody) {
      var content = endpoint.value.requestBody?.content
      var schema = content['application/json']?.schema || content['multipart/form-data']?.schema
      if ('$ref' in schema) {
        var ref = schema.$ref.split('/').slice(-1)[0]
        schema = toc.value.components?.schemas[ref]
      }
      var required = schema?.required || []
      for (var [name, meta] of Object.entries(schema?.properties || {})) {
        var type = meta.type || meta.anyOf[0]?.type
        result.push({name:name, type:type, in:'body',
          required:required.includes(name), description:meta.description})
      }
    }
    return result
  })

  // On Mounted
  // Set topnav and fetch toc
  onMounted(async function() {
    utils.setNavPosition('top')
    toc.value = (await axios.get(APIROOT)).data
    setupRequest(path.value || APIROOT, method.value || 'get')
  })

  // Create Example Schema
  // Creates an example schema from the schema object
  const createExampleSchema = function(schema) {
    if ('$ref' in schema) {
      var ref = schema.$ref.split('/').slice(-1)[0]
      schema = toc.value.components?.schemas[ref]
    }
    var result = {}
    for (var [pname, properties] of Object.entries(schema.properties || {})) {
      var ptype = properties.type || properties.anyOf[0]?.type
      var pvalue = {'string':'string', 'number':1, 'boolean':true, 'object':{}, 'array':[]}[ptype]
      console.log('pname', pname, 'ptype', ptype, 'pvalue', pvalue)
      result[pname] = pvalue
    }
    return result
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
        if (newpath.startsWith('/api/')) { setupRequest(newpath, 'get') }
        else { window.open(newpath, '_blank') }
      })
      span.replaceWith(newspan)
    })
  }

  // Watch _Path
  // Watch the _path value and update the request
  watch(_path, function(newpath) {
    setupRequest(newpath, method.value, null, false)
  })

  // Paths Match
  // Check the two paths match
  const pathMatches = function(pathstr, endptstr) {
    if (endptstr.includes('/api/')) { endptstr = endptstr.split('/api/')[1] }
    if (pathstr.includes('/api/')) { pathstr = pathstr.split('/api/')[1] }
    if (pathstr.includes('?')) { pathstr = pathstr.split('?')[0] }
    var pattern = endptstr.replace(/{\w+}/g, '[^/]+').replace(/\//g, '\\/')
    return new RegExp(`^${pattern}$`).test(pathstr)
  }

  // Set Path
  // Update path and method from the endpoint path
  const setupRequest = function(newpath, newmethod, newpayload=null, autoRequest=true) {
    console.log(`setupRequest(${newpath}, ${newmethod}, <payload>, ${autoRequest})`)
    // Close any tooltips and clear the response
    historyTooltip.value?.close()
    response.value = null
    // Update method, path, and payload
    method.value = newmethod.toLowerCase()
    path.value = newpath.startsWith('http') ? decodeURIComponent(new URL(newpath).pathname) : newpath
    payload.value = newpayload ? utils.stringify(JSON.parse(newpayload), {indent:2}) : null
    _path.value = path.value
    // Update the endpoint, check current method allowed, check send request
    updateEndpoint()
    // console.log('endpoint:', endpoint.value)
    if (!allowed.value.includes(method.value)) { method.value = allowed.value[0] }
    if (autoRequest) { checkSendRequest() }
  }

  // Check Auto Request
  // Check if we want to auto send the request
  const checkSendRequest = function() {
    // if (response.value) { return }
    if (!path.value || !method.value || !endpoint.value) { return }
    if (method.value != 'get' || path.value.includes('{')) { return }
    sendRequest()
  }

  // Send Request
  // Send the http request
  const sendRequest = async function() {
    if (!path.value) { return }
    loading.value = true
    var data = (method.value != 'get') ? JSON.parse(payload.value) || {} : undefined
    await axios[method.value.toLowerCase()](path.value, data)
      .then(resp => response.value = resp)
      .catch(err => response.value = err.response)
      .finally(() => loading.value = false)
    await nextTick()
    linkResponseUrls()
  }

  // Update Endpoint & Allowed Methods
  // Updates the current endpoint and allowed methods
  const updateEndpoint = function() {
    var endpt = null
    var methods = []
    for (const [epath, endpts] of Object.entries(toc.value.paths)) {
      for (const [emethod, details] of Object.entries(endpts)) {
        if (pathMatches(path.value, epath)) {
          methods.push(emethod)
          if (method.value == emethod) {
            var category = epath.replace('/api/', '').split('/')[0] || 'root'
            endpt = endpt || {...details, path:epath, method:emethod, category:category}
          }
        }
      }
    }
    endpoint.value = endpt
    allowed.value = methods.length ? methods : ['get']
    // Check we need a payload and its not already set
    if (!payload.value && ['post', 'patch'].includes(method.value)) {
      var schema = endpoint.value.requestBody?.content['application/json']?.schema || {}
      payload.value = utils.stringify(createExampleSchema(schema))
    }
  }
</script>

<style>
  #apidoc {
    /* Header and API Options */
    .description {
      font-size: 13px;
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
      .payloadwrap {
        position: relative;
        .codeeditor {
          font-size: 12px;
        }
        .send-request {
          position: absolute;
          bottom: 4px;
          right: 10px;
          z-index: 9;
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

    /* Code Editor */
    .codeeditor {
      font-size: 11px;
      .link {
        cursor: pointer;
        transition: color 0.3s;
        &:hover { color:var(--fgcolor); }
      }
    }
  }
</style>

