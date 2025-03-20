<template>
  <div class='datatable'>
    <table v-if='items !== null'>
      <thead>
        <tr><slot name='headers'></slot></tr>
        <tr v-if="$slots.headerrow"><slot name='headerrow'></slot></tr>
      </thead>
      <tbody>
        <tr v-for='item in items' :key='item[keyattr]'>
          <slot name='columns' :item="item"></slot>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
  const props = defineProps({
    items: {type:Array, required:true},
    keyattr: {type:String, required:true},
  })
</script>

<style>
  .datatable {
    border: 1px solid var(--lightbg-bg3);
    border-radius: 6px;
    padding: 1px;
    table {
      border-collapse: collapse;
      border-spacing: 0;
      width: 100%;
    }
    th, td { padding: 1px 6px; }
    th { background-color: #eaeae7; }
    td { border-top: 1px solid var(--lightbg-bg3); } 
    .thwrap {
      font-family: var(--fontfamily-title);
      font-size: 12px;
      font-weight: bold;
      color: var(--lightbg-fg2);
      text-align: left;
    }
    .tdwrap {
      font-size: 13px;
    }
  }
</style>
