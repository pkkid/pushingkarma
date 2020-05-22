<template>
  <transition name='custom-classes-transition' enter-active-class='animated fadeIn'>
    <div id='events' v-if='events'>
      <div v-if='events && events.length'>
        <div class='title'>Upcoming Events</div>
        <div class='event' v-for='event in events.slice(0,3)' :key='event.id' :class={soon:event.soon}>
          <div class='subject'>{{event.Subject}}</div>
          <div class='details'>
            {{ event.Start | formatDate('h:mm') }} - {{ event.End | formatDate('h:mm') }}
            <span v-if='event.Location.DisplayName'>| <span v-html='linkZoom(event.Location.DisplayName)'/></span>
          </div>
        </div>
      </div>
      <div v-else class='noevents'>No events</div>
    </div>
  </transition>
</template>

<script>
  import * as api from '@/api';
  import * as dayjs from 'dayjs';

  export default {
    name: 'NewTabEvents',
    data: () => ({
      events: null,
    }),
    mounted: function() {
      this.update();
      setInterval(this.update, 1000*60);
    },
    methods: {
      update: async function() {
        var events = [];
        var {data} = await api.Tools.getEvents();
        var now = dayjs();
        var soon = dayjs().add(5, 'minutes');
        var max = dayjs().add(12, 'hours');
        for (var event of data) {
          var start = dayjs(event.Start);
          var end = dayjs(event.End).subtract(10, 'minutes');
          if ((end > now) && (start < max)) {
            if (soon > start) { event.soon = true; }
            events.push(event);
          }
        }
        this.events = events;
      },

      // Replace zoom urls with links
      linkZoom: function(location) {
        return location.replace(/(https*:\/\/\w*\.zoom\.us\/j\/\d+\?\w+=\w+)/g, '<a href="$1">Zoom</a>');
      },
    }
  };
</script>

<style lang='scss'>
  #events {
    left: 15px;
    position: absolute;
    top: 20px;
    width: 400px;
    .title {
      border-bottom: 1px solid rgba(255,255,255,0.3);
      color: $newtab_dim;
      font-size: 16px;
      font-weight: 400;
      margin-bottom: 0px;
      margin-left: 5px;
    }
    .event {
      padding:2px 5px 0px 5px;
      margin-top: 2px;
      border-radius: 3px;
      &.soon {
        background-color: #222;
        animation-name: color;
        animation-duration: 2s;
        animation-iteration-count: infinite;
      }
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
      a,a:visited {
        background-color: rgba(255,255,255,0);
        color: $newtab_dim;
        padding: 1px 2px 0px 2px;
        border-radius: 3px;
      }
      a:hover {
        color:#fff;
        background-color: rgba(255,255,255,0.3);
      }
    }
    .noevents {
      color: rgba(255,255,255,0.3);
      font-size: 20px;
      text-shadow: none;
    }
  }
  @keyframes color {
    0% { background-color: transparent; }
    50% { background-color: rgba(255,0,0,0.3) }
    100% { background-color: transparent; }
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
