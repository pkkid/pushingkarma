<template>
  <div id='tasks'>
    {#if tasks.length}
      <div class='title'>My Tasks</div>
      {#withBefore tasks 4}
        <div class='task'>{this.title}</div>
      {/withBefore}
    {else}
      <div class='notasks'>
        No tasks
      </div>
    {/if}
  </div>
</template>

<script>
  export default {
    name: 'NewTabTasks',
  };
</script>

<style lang='scss'>
</style>
