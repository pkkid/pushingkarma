<template>
  <div id='calendar'>
    {#if events.length}
      <div class='title'>Upcoming Events</div>
      {#withBefore events 3}
        <div class='event'>
          <div class='subject'>{this.Subject}</div>
          <div class='details'>
            {formatDate this.Start '%l:%M'} - {formatDate this.End '%l:%M'}
            {#if this.Location.DisplayName}| {this.Location.DisplayName}{/if}
          </div>
        </div>
      {/withBefore}
    {else}
      <div class='noevents'>
        No events
      </div>
    {/if}
  </div>
</template>

<script>
  export default {
    name: 'NewTabCalendar',
  };
</script>

<style lang='scss'>
</style>
