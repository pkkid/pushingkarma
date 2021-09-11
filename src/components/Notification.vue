<template>
  <div id='notifications'>
    <transition-group name='custom-classes-transition'
      enter-active-class='animated flipInX'
      leave-active-class='animated fadeOutUp'>
      <div class='notification' v-for='msg in messages' :key='msg.msgid'>
        <div class='title'><i class='mdi' :class='msg.icon'/> {{msg.title}}</div>
        <div class='message' v-if='msg.message'>{{msg.message}}</div>
      </div>
    </transition-group>
  </div>
</template>

<script>
  export default {
    name: 'Notification',
    data: () => ({
      msgid: 0,
      messages: [],
      timeout: 5000,
    }),
    mounted: function() {
      var self = this;
      this.$root.$on('notify', function(title, message, icon) {
        self.msgid += 1;
        console.log(`[${self.msgid}] ${title}. ${message}`);
        self.messages.push({msgid:self.msgid, title:title, message:message, icon:icon});
        console.log(self.messages);
        setTimeout(() => delete self.messages.shift(), self.timeout);
      });
    },
  };
</script>

<style lang='scss'>
  #notifications {
    position: fixed;
    right: 20px;
    top: 80px;
    width: 300px;
    z-index: 101;
    .notification {
      animation-duration: 0.6s;
      background-color: #111;
      border-radius: 4px;
      box-shadow: 0 2px 3px rgba(0, 0, 0, .5);
      font-size: 1rem;
      margin-bottom: 10px;
      padding: 8px 20px 10px 15px;
    }
    .mdi {
      font-size: 1.1em;
      margin-right: 5px;
      position: relative;
      top: 1px;
    }
    .title {
      font-size: 1.1em;
      font-weight: 500;
      color: $darkbg-text;
      margin-bottom: 2px;
    }
    .message {
      font-size: 0.9em;
      font-weight: normal;
      background-color: transparent;
      color: $darkbg-text;
      margin-left: 28px;
    }
  }
</style>
