<template>
  <transition name='custom-classes-transition' enter-active-class='animated fadeIn'>
    <div id='events' v-if='events'>
      <div v-if='events'>
        <div class='title'>Upcoming Events</div>
        <div class='event' v-for='event in events.slice(0,3)' :key='event.id'>
          <div class='subject'>{{event.Subject}}</div>
          <div class='details'>
            {{ event.Start | formatDate('h:mm') }} - {{ event.End |formatDate('h:mm') }}
            <span v-if='event.Location.DisplayName'>| {{event.Location.DisplayName}}</span>
          </div>
        </div>
      </div>
      <div v-else class='notasks'>No events</div>
    </div>
  </transition>
</template>

<script>
  import * as api from '@/api';
  

  export default {
    name: 'NewTabEvents',
    data: () => ({
      events: null,
    }),
    mounted: function() {
      this.update();
      setInterval(this.update, 1000*60*5);
    },
    methods: {
      update: async function() {
        var {data} = await api.Tools.getEvents();
        this.events = data;
      }
    }
  };
</script>

<style lang='scss'>
  #events {
    left: 20px;
    position: absolute;
    top: 20px;
    width: 400px;
    .title {
      border-bottom: 1px solid rgba(255,255,255,0.3);
      color: $newtab_dim;
      font-size: 16px;
    }
    .event {
      margin-top:3px;
    }
    .subject {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .details {
      color: $newtab_dim;
      font-size: 12px;
      overflow: hidden;
      position: relative;
      text-overflow: ellipsis;
      top: -5px;
      white-space: nowrap;
    }
    .noevents {
      color: rgba(255,255,255,0.3);
      font-size: 20px;
      text-shadow: none;
    }
  }
  @media screen and (max-width: 1100px) {
    #events { left:20px; top:140px; width:400px; }
  }
  @media screen and (max-width: 800px) {
    #events {
      .title { color: $raspi_dim; }
      .details { color: $raspi_dim; }
    }
  }
</style>
