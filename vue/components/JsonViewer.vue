<template>
  <span class='json-node'>
    <!-- Collection: Object or Array -->
    <template v-if='isCollection'>
      <!-- Empty collection -->
      <span v-if='collectionSize === 0'>
        <span class='json-arrow-placeholder'/>
        <span v-if='keyName !== undefined' class='json-key'>
          "{{keyName}}"<span class='json-punct'>: </span>
        </span>
        {{openBracket}}{{closeBracket}}
      </span>
      <!-- Expanded collection -->
      <template v-else-if='isOpen'>
        <span class='json-arrow' @click.stop='handleToggle'>▶</span>
        <span v-if='keyName !== undefined' class='json-key'>
          "{{keyName}}"<span class='json-punct'>: </span>
        </span>
        {{openBracket}}
        <span class='json-block'>
          <JsonViewer v-for='entry in entries' :key='entry.key' :value='entry.value'
            :keyName='isObject ? String(entry.key) : undefined' :isLast='entry.isLast'
            :depth='depth + 1' :registerSetter='registerChildSetter'
            :ctrlToggle='ctrlToggleChildren' />
        </span>
        {{closeBracket}}<span v-if='!isLast' class='json-punct'>,</span>
      </template>
      <!-- Collapsed collection -->
      <template v-else>
        <span class='json-arrow json-collapsed' @click.stop='handleToggle'>▶</span>
        <span v-if='keyName !== undefined' class='json-key'>"{{keyName}}"<span class='json-punct'>: </span></span>
        <span class='json-collapsed-body' @click.stop='handleToggle'>
          {{openBracket}}
          <span class='json-summary'> … {{collectionSize}} {{itemLabel}}</span>
          {{closeBracket}}
        </span>
        <span v-if='!isLast' class='json-punct'>,</span>
      </template>
    </template>

    <!-- Primitive value -->
    <template v-else>
      <span class='json-arrow-placeholder'/>
      <span v-if='keyName !== undefined' class='json-key'>"{{keyName}}"<span class='json-punct'>: </span></span>
      <a v-if='isUrl' :href='value' target='_blank' class='json-string json-url'>{{displayValue}}</a>
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
    registerSetter: {type:Function, default:null},
    ctrlToggle: {type:Function, default:null},
  })

  const isString = computed(() => typeof props.value === 'string')
  const isNumber = computed(() => typeof props.value === 'number')
  const isBoolean = computed(() => typeof props.value === 'boolean')
  const isNull = computed(() => props.value === null)
  const isArray = computed(() => Array.isArray(props.value))
  const isObject = computed(() => !isArray.value && typeof props.value === 'object' && props.value !== null)
  const isCollection = computed(() => isArray.value || isObject.value)
  const isUrl = computed(() => isString.value && (props.value.startsWith('http://') || props.value.startsWith('https://')))
  const collectionSize = computed(() => {
    if (isArray.value) return props.value.length
    if (isObject.value) return Object.keys(props.value).length
    return 0
  })
  const openBracket = computed(() => isArray.value ? '[' : '{')
  const closeBracket = computed(() => isArray.value ? ']' : '}')
  const itemLabel = computed(() => {
    const n = collectionSize.value
    return isArray.value ? (n === 1 ? 'item' : 'items') : (n === 1 ? 'key' : 'keys')
  })
  const isOpen = ref(props.depth < 2)

  // Display Value
  // For strings, we want to show them with quotes and escaped characters.
  // For other primitives, just show the value.
  const displayValue = computed(() => {
    if (isNull.value) return 'null'
    if (isBoolean.value) return String(props.value)
    if (isNumber.value) return String(props.value)
    if (isString.value) {
      const escaped = props.value
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r')
        .replace(/\t/g, '\\t')
      return `"${escaped}"`
    }
    return ''
  })

  // Primitive Class
  // Determine the CSS class for primitive values based on their type.
  const primitiveClass = computed(() => {
    if (isString.value) return 'json-string'
    if (isNumber.value) return 'json-number'
    if (isBoolean.value) return 'json-boolean'
    if (isNull.value) return 'json-null'
    return ''
  })

  // Child state management for ctrl+click siblings behavior.
  // registerChildSetter returns an unregister fn so stale setters are cleaned up.
  const childSetters = []
  const registerChildSetter = (setter) => {
    childSetters.push(setter)
    return () => {
      const idx = childSetters.indexOf(setter)
      if (idx >= 0) childSetters.splice(idx, 1)
    }
  }
  const ctrlToggleChildren = (targetOpen) => childSetters.forEach(s => s(targetOpen))

  // Register this node's open state with its parent (for ctrl+click)
  const setOpen = (v) => { isOpen.value = v }
  var _unregister = null
  onMounted(() => { if (props.registerSetter) _unregister = props.registerSetter(setOpen) })
  onUnmounted(() => { if (_unregister) _unregister() })

  // Handle Toggle
  // Toggle open/closed. Ctrl+click toggles all siblings at this level.
  const handleToggle = (e) => {
    if (collectionSize.value === 0) return
    if (e.ctrlKey && props.ctrlToggle) {
      props.ctrlToggle(!isOpen.value)
    } else {
      isOpen.value = !isOpen.value
    }
  }

  // Entries
  // For collections, create an array of entries with key, value,
  // and isLast for rendering.
  const entries = computed(() => {
    if (isArray.value) {
      return props.value.map((v, i) => ({key:i, value:v, isLast:i === props.value.length - 1}))
    }
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
    position: relative;
    font-family: var(--fontfamily-code);
    font-size: 11px;
    line-height: 1.3em;
    color: #504945;
  }
  .json-key { color: #af3a03; }
  .json-string { color: #79740e; }
  .json-number { color: #076678; }
  .json-boolean { color: #af3a03; }
  .json-null { color: #af3a03; }
  .json-url { color: #076678; }
  .json-punct { color: #504945; }
  .json-summary { color: #a89984; }

  .json-arrow, .json-arrow-placeholder {
    position: absolute;
    left: -13px;
    display: inline-block;
    width: 1.2em;
    font-size: 10px;
  }
  .json-arrow {
    cursor: pointer;
    user-select: none;
    opacity: 0.5;
    transform: rotate(90deg);
    transition: transform 0.15s ease, opacity 0.15s ease;
  }
  .json-arrow.json-collapsed {
    transform: rotate(0deg);
  }
  .json-arrow:hover {
    opacity: 1;
  }
  .json-collapsed-body {
    cursor: pointer;
    user-select: none;
  }

  .json-block {
    display: block;
    margin-left: 0.3em;
    padding-left: 1.5em;
    border-left: 1px dotted #0002;
  }
</style>
