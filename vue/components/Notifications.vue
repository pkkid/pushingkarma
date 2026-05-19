<template>
  <div id='notifications'>
    <TransitionGroup name='fade' tag='div'>
      <div v-for='(notification, index) in notifications' :key='index' class='notification darkbg'>
        <i class='close mdi mdi-close' @click='removeNotification(index)'/>
        <i v-if='notification.icon' class='icon mdi' :class='notification.icon' />
        <div class='title'>{{ notification.title }}</div>
        <div class='message'>{{ notification.message }}</div>
        <div v-if='notification.actions?.length' class='actions'>
          <button v-for='(action, i) in notification.actions' :key='i' class='actionbtn' @click='runAction(index, action)'>
            <div>{{ action.label }}</div>
            <div v-if='action.hotkeyLabel' class='subtext'>{{ action.hotkeyLabel }}</div>
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
  import {onBeforeUnmount, onMounted, reactive} from 'vue'
  const notifications = reactive([])

  // Add Notification
  // Display a new notification
  const notify = function(title, message, icon=null, duration=30000, actions=[]) {
    const id = Math.random().toString(36).substring(2, 15)
    const notification = {title, message, icon, actions, id}
    // Add new notification to the first position
    notifications.unshift(notification)
    if (duration > 0) {
      setTimeout(function() {
        const index = notifications.findIndex(n => n.id == id)
        if (index != -1) { notifications.splice(index, 1) }
      }, duration)
    }
  }

  // Remove Notification
  // Closes and removes the notification
  function removeNotification(index) {
    notifications.splice(index, 1)
  }

  // Run Action
  // Trigger an inline action for a notification
  async function runAction(index, action) {
    if (action?.closeOnClick !== false) {
      removeNotification(index)
    }
    await action?.onClick?.()
  }

  // Matches Hotkey
  // Returns true when key event matches a configured hotkey object
  const matchesHotkey = function(event, hotkey) {
    if (!hotkey?.key) { return false }
    var key = event.key?.toLowerCase()
    if (key != hotkey.key.toLowerCase()) { return false }
    if (!!hotkey.altKey != event.altKey) { return false }
    if (!!hotkey.ctrlKey != event.ctrlKey) { return false }
    if (!!hotkey.metaKey != event.metaKey) { return false }
    if (!!hotkey.shiftKey != event.shiftKey) { return false }
    return true
  }

  // On Keydown
  // Runs the first matching shortcut for the most recent notification
  const onKeydown = async function(event) {
    if (!notifications.length) { return }
    var topNotification = notifications[0]
    if (!topNotification?.actions?.length) { return }
    var action = topNotification.actions.find(action => matchesHotkey(event, action.hotkey))
    if (!action) { return }
    event.preventDefault()
    event.stopPropagation()
    await runAction(0, action)
  }

  onMounted(function() {
    window.addEventListener('keydown', onKeydown)
  })

  onBeforeUnmount(function() {
    window.removeEventListener('keydown', onKeydown)
  })

  // Define Exposed
  defineExpose({notify})
</script>

<style scoped>
  #notifications {
    
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 110;
    width: 400px;
    & > div {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .notification {
      border-radius: 6px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
      font-size: 13px;
      padding: 20px;
      position: relative;
      border: 1px solid var(--lightbg-fg1);
      width: 100%;
      .icon { font-size:20px; float:left; }
      .title {
        margin: 0px 30px 0px 30px;
        font-family: var(--fontfamily-title);
        font-weight: bold;
      }
      .message {
        margin: 0px 20px 0px 30px;
        font-family: var(--fontfamily-article);
      }
      .actions {
        display: flex;
        gap: 8px;
        margin: 12px 0px 0px 30px;
      }
      .actionbtn {
        background: var(--lightbg-fg1);
        border: 0;
        border-radius: 4px;
        color: var(--darkbg-fg1);
        cursor: pointer;
        font-family: var(--fontfamily-title);
        font-size: 11px;
        padding: 5px 10px;
        opacity: 0.7;
        text-align: left;
        .subtext {
          margin-top: 3px;
        }
      }
      .actionbtn:hover {
        background: var(--lightbg-fg2);
        opacity: 1;
      }
    }
    .close {
      position: absolute;
      right: 15px;
      top: 15px;
      font-size: 16px;
    }
  }
</style>
