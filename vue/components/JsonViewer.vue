<template>
  <span class='json-node'>
    <!-- Arrow (or placeholder) -->
    <span v-if='collectionSize > 0' class='json-arrow' :class='{collapsed: !isOpen}' @click.stop='handleToggle'>▶</span>
    <span v-else class='json-arrow-placeholder'/>
    <!-- Key Label -->
    <span v-if='keyName !== undefined' class='json-key'>"{{keyName}}"<span class='json-punct'>: </span></span>
    <!-- Collection -->
    <template v-if='isCollection'>
      <template v-if='collectionSize === 0'>{{openBracket}}{{closeBracket}}</template>
      <template v-else-if='isOpen'>
        {{openBracket}}
        <span class='json-block'>
          <JsonViewer v-for='entry in entries' :key='entry.key' :value='entry.value'
            :keyName='isObject ? String(entry.key) : undefined' :isLast='entry.isLast'
            :depth='depth + 1' :registerSetter='registerChildSetter' :ctrlToggle='ctrlToggleChildren'
            :urlHandler='urlHandler'/>
        </span>
        {{closeBracket}}<span v-if='!isLast' class='json-punct'>,</span>
      </template>
      <template v-else>
        <span class='json-collapsed-body' @click.stop='handleToggle'>{{openBracket}}<span class='json-summary'> … {{collectionSize}} {{itemLabel}}</span>{{closeBracket}}</span><span v-if='!isLast' class='json-punct'>,</span>
      </template>
    </template>
    <!-- Primitive -->
    <template v-else>
      <span v-if='isUrl' class='json-string json-url' @click='handleUrlClick'>{{displayValue}}</span>
      <span v-else :class='primitiveClass'>{{displayValue}}</span>
      <span v-if='!isLast' class='json-punct'>,</span>
    </template>
  </span>
</template>

<script setup>
  import {computed, onMounted, onUnmounted, ref} from 'vue'
  import JsonViewer from './JsonViewer.vue'

  const props = defineProps({
    value: {},
    keyName: {type:String, default:undefined},
    isLast: {type:Boolean, default:true},
    depth: {type:Number, default:0},
    urlHandler: {type:Function, default:null},
    registerSetter: {type:Function, default:null},
    ctrlToggle: {type:Function, default:null},
  })

  // Computed State
  const isOpen = ref(true)
  const isArray = computed(() => Array.isArray(props.value))
  const isObject = computed(() => !isArray.value && typeof props.value === 'object' && props.value !== null)
  const isCollection = computed(() => isArray.value || isObject.value)
  const isUrl = computed(() => typeof props.value === 'string' && (props.value.startsWith('http://') || props.value.startsWith('https://')))
  const collectionSize = computed(() => isArray.value ? props.value.length : isObject.value ? Object.keys(props.value).length : 0)
  const openBracket = computed(() => isArray.value ? '[' : '{')
  const closeBracket = computed(() => isArray.value ? ']' : '}')
  const primitiveClass = computed(() => props.value === null ? 'json-null' : `json-${typeof props.value}`)
  const itemLabel = computed(() => {
    const n = collectionSize.value
    return isArray.value ? (n === 1 ? 'item' : 'items') : (n === 1 ? 'key' : 'keys')
  })
  const displayValue = computed(() => {
    if (typeof props.value !== 'string') return String(props.value)
    return '"' + props.value
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/\n/g, '\\n')
      .replace(/\r/g, '\\r')
      .replace(/\t/g, '\\t') + '"'
  })
  
  const handleUrlClick = () => {
    if (props.urlHandler) props.urlHandler(props.value)
    else window.open(props.value, '_blank')
  }

  // Child State Management
  // RegisterChildSetter returns an unregister fn to avoid stale setters
  const childSetters = []
  const registerChildSetter = (setter) => {
    childSetters.push(setter)
    return () => { const i = childSetters.indexOf(setter); if (i >= 0) childSetters.splice(i, 1) }
  }
  const ctrlToggleChildren = (targetOpen) => childSetters.forEach(s => s(targetOpen))

  // Register With Parent
  // Allows ctrl+click can toggle siblings
  const setOpen = (v) => { isOpen.value = v }
  var _unregister = null
  onMounted(() => { if (props.registerSetter) _unregister = props.registerSetter(setOpen) })
  onUnmounted(() => { if (_unregister) _unregister() })

  // Handle Toggle
  // Holding ctrl will also toggle all siblings
  const handleToggle = (e) => {
    if (e.ctrlKey && props.ctrlToggle) props.ctrlToggle(!isOpen.value)
    else isOpen.value = !isOpen.value
  }

  // Entries
  // Get entries for v-for loop; also marks last entry for comma placement
  const entries = computed(() => {
    if (isArray.value) return props.value.map((v, i) => ({key:i, value:v, isLast:i === props.value.length - 1}))
    if (isObject.value) {
      const keys = Object.keys(props.value)
      return keys.map((k, i) => ({key:k, value:props.value[k], isLast:i === keys.length - 1}))
    }
    return []
  })
</script>

<style scoped>
  .json-node {
    display: block;
    font-family: var(--fontfamily-code);
    font-size: 11px;
    line-height: 1.3em;
    padding-left: 0.2em;
    color: #504945;
  }
  .json-key { color: #af3a03; }
  .json-string { color: #79740e; }
  .json-number { color: #076678; }
  .json-boolean { color: #af3a03; }
  .json-null { color: #af3a03; }
  .json-punct { color: #504945; }
  .json-summary { color: #a89984; }
  .json-url {
    color: #076678;
    cursor: pointer;
    transition: color 0.15s ease;
    &:hover { color:#000; }
  }
  .json-arrow,
  .json-arrow-placeholder {
    position: relative;
    margin-left: -15px;
    display: inline-block;
    width: 1.3em;
    font-size: 10px;
  }
  .json-arrow {
    cursor: pointer;
    user-select: none;
    opacity: 0.5;
    position: relative;
    left: -2px;
    transform: rotate(90deg);
    transition: transform 0.15s ease, opacity 0.15s ease;
    &.collapsed { transform: rotate(0deg); left: 0px; }
    &:hover { opacity: 1; }
  }
  .json-collapsed-body {
    cursor: pointer;
    user-select: none;
  }
  .json-block {
    display: block;
    margin-left: 0em;
    padding-left: 1.5em;
    border-left: 1px dotted #0002;
  }
</style>
