<template>
  <transition name='custom-classes-transition' enter-active-class='animated fadeIn'>
    <div id='tasks' v-if='tasks'>
      <div v-if='tasks'>
        <div class='title'>My Tasks</div>
        <div class='task' v-for='task in tasks.slice(0,4)' :key='task.id'>
          {{task.title}}
        </div>
      </div>
      <div v-else class='notasks'>No tasks</div>
    </div>
  </transition>
</template>

<script>
  import * as api from '@/api';

  export default {
    name: 'NewTabTasks',
    data: () => ({
      tasks: null,
    }),
    mounted: async function() {
      this.update();
      setInterval(this.update, 1000*60*5);
    },
    methods: {
      update: async function() {
        var {data} = await api.Tools.getTasks();
        this.tasks = data;
      }
    }
  };
</script>

<style lang='scss'>
  #tasks {
    bottom: 20px;
    position: absolute;
    right: 20px;
    transition: $newtab_transition_fast;
    width: 275px;
    .title {
      border-bottom: 1px solid rgba(255,255,255,0.3);
      color: $newtab_dim;
      font-size: 16px;
      margin-bottom: 3px;
      font-weight: 400;
      line-height: 1.5;
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
        top: 6px;
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
  @media screen and (max-width: 1100px) {
    #tasks { right:20px; left:auto; top:190px; width:275px; }
  }
  @media screen and (max-width: 800px) {
    #tasks {
      .title { color: $raspi_dim; }
      .task:before { border: 2px solid $raspi_dim; }
    }
  }
</style>
