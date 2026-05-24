<template>
  <div class='payee-tooltip'>
    <div class='title'>{{trx.original_payee}}</div>
    <transition name='fade' mode='out-in' :style='`transition-duration:${transitionDuration}`'>
      <div v-if='responseHtml' class='details' v-html='responseHtml'/>
      <div v-else-if='error' class='error'>{{error}}</div>
      <IconMessage v-else-if='loading' icon='pk' iconsize='25px' height='50px'
        animation='gelatine' color='var(--darkbg-fg3)' ellipsis/>
      <a v-else href='#' @click.prevent='requestDetails'>Request Details</a>
    </transition>
  </div>
</template>

<script setup>
  import {computed, onBeforeUnmount, onMounted, ref} from 'vue'
  import {IconMessage} from '@/components'
  import {api, utils} from '@/utils'

  const props = defineProps({
    trx: {type:Object, required:true},    // Transaction object
  })
  var transitionDuration = ref('0s')      // CSS variable for transition duration
  var cancelctrl = null                   // Controller for cancelling API request
  const loading = ref(false)              // True if waiting for API response
  const response = ref(null)              // AI response string
  const error = ref(null)                 // Error message if API request fails

  // Response HTML
  // Convert newlines to <br> and escape HTML
  const responseHtml = computed(function() {
    if (!response.value) { return null }
    return utils.escapeHtml(response.value).replace(/\n/g, '<br>')
  })

  // Build Payee Prompt
  // The exact prompt sent to /api/main/aiprompt for payee lookup
  const buildPrompt = function() {
    return utils.dedent(`
      You are helping me classify and understand a financial transaction payee.
      Give a concise response in one to sentences explaining the likley merchant
      or business name and type of expense this usually is. Do not use any markdown
      or formatting, just plain text. No need to say "this transaction is" or "this
      payment is for" or similar, just get straight to the point of who the merchant
      is and what the charge or payback likley represents.

      Transaction context:
      - Payee: ${props.trx.payee || '(empty)'}

      If uncertain, say so clearly and avoid making up specific facts.
    `).trim()
  }

  // Check Cache
  // On mount, silently check if the backend already has a cached response for this payee
  const checkCache = async function() {
    try {
      var prompt = {prompt: buildPrompt()}
      var params = {cache_only:true}
      var {data} = await api.Main.aiPrompt(prompt, params)
      response.value = data?.response?.trim() || null
    } finally {
      transitionDuration.value = '0.2s'
    }
  }

  // Request Details
  // User opted in — call the AI endpoint and wait for the full response
  const requestDetails = async function() {
    if (loading.value || response.value) { return }
    loading.value = true
    error.value = null
    cancelctrl = api.cancel(cancelctrl)
    try {
      var prompt = {prompt: buildPrompt()}
      var {data} = await api.Main.aiPrompt(prompt, null, cancelctrl.signal)
      response.value = data.response?.trim() || 'No response.'
    } catch (err) {
      if (api.isCancel(err)) { return }
      error.value = err.response?.data?.detail || err.message || 'Unable to request details.'
    } finally {
      loading.value = false
    }
  }

  onMounted(function() { checkCache() })
  onBeforeUnmount(function() { api.cancel(cancelctrl) })
</script>

<style>
  .payee-tooltip {
    .title {
      width: 100%;
      border-bottom: 1px dotted #fff3;
      padding-bottom: 4px;
      margin-bottom: 4px;
    }
  }
</style>
