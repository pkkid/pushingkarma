<template>
  <div id='notifications'>
    <TransitionGroup name='fade' tag='div'>
      <div v-for='(notification, index) in notifications' :key='index' class='notification darkbg'>
        <i class='close mdi mdi-close' @click='removeNotification(index)'/>
        <i v-if='notification.icon' class='icon mdi' :class='notification.icon' />
        <div class='title'>{{ notification.title }}</div>
        <div class='message'>{{ notification.message }}</div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
  import {reactive} from 'vue'
  const notifications = reactive([])

  // Add Notification
  // Display a new notification
  const notify = function(title, message, icon=null, duration=5000) {
    const id = Math.random().toString(36).substring(2, 15)
    const notification = {title, message, icon, id}
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

  // Define Exposed
  defineExpose({notify})
</script>

<style scoped>
  #notifications {
    
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 98;
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
    }
    .close {
      position: absolute;
      right: 15px;
      top: 15px;
      font-size: 16px;
    }
  }
</style>
