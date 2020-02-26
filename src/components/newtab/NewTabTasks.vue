<template>
  <div v-if='tasks' id='tasks'>
    <div class='title'>My Tasks</div>
    <div class='task' v-for='task in tasks.slice(0,4)' :key='task.id'>
      {{task.title}}
    </div>
  </div>
  <div v-else id='tasks'>
    <div class='notasks'>No tasks</div>
  </div>
</template>

<script>
  import * as api from '@/api';

  export default {
    name: 'NewTabTasks',
    data: () => ({
      tasks: null,
    }),
    mounted: async function() {
      var {data} = await api.Tools.getTasks();
      this.tasks = data;
      console.log(this.tasks);
    },
  };
</script>

<style lang='scss'>
  #tasks {
    background-color: $newtab_highlight;
    bottom: 20px;
    position: absolute;
    right: 20px;
    transition: $newtab_transition_slow;
    width: 275px;
    .title {
      border-bottom: 1px solid rgba(255,255,255,0.3);
      color: $newtab_dim;
      font-size: 16px;
      margin-bottom: 3px;
    }
    .task {
      position: relative;
      padding-left: 20px;
      &:before {
        content: ' ';
        position: absolute;
        border: 2px solid $newtab_dim;
        border-radius: 3px;
        width: 10px;
        height: 10px;
        top: 7px;
        left: 3px;
      }
    }
    .notasks {
      color: rgba(255,255,255,0.3);
      font-size: 20px;
      text-shadow: none;
      text-align: right;
    }
  }
</style>
