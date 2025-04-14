<template>
  <div id='notifications'>
    <div v-for='(notification, index) in notifications' :key='index' class='notification darkbg'>
      <i v-if='notification.icon' :class='notification.icon' />
      <div class='message'>{{ notification.message }}</div>
      <button class='close' @click='removeNotification(index)'>x</button>
    </div>
  </div>
</template>

<script setup>
  import {reactive} from 'vue'
  const notifications = reactive([])

  // Add Notification
  // Display a new notification
  const notify = function(message, duration=5000, icon=null) {
    const notification = {message, duration, icon}
    notifications.push(notification)
    if (duration > 0) {
      setTimeout(function() {
        const index = notifications.indexOf(notification)
        if (index !== -1) notifications.splice(index, 1)
      }, duration)
    }
  }

  // Remove Notification
  // Closes and removes the notification
  function removeNotification(index) {
    notifications.splice(index, 1)
  }

  // Define Exposed
  defineExpose({notify})
</script>

<style scoped>
  #notifications {
    display: flex;
    flex-direction: column;
    gap: 15px;
    position: fixed;
    top: 20px; right: 20px;
    z-index: 98;

    .notification {
      background: var(--bgcolor);
      color: var(--fgcolor);
      padding: 1rem;
      border-radius: 0.5rem;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .close {
      background: none;
      border: none;
      color: var(--fgcolor);
      font-size: 1.2rem;
      cursor: pointer;
    }
    .notification i {
      font-size: 1.5rem;
    }
  }
</style>
