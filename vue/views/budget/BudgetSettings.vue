<template>
  <LayoutPaper id='budgetsettings' width='900px'>
    <template #content>
      <h1>Budget Settings</h1>
      <!-- Accounts -->
      <h2>Accounts</h2>
      <div class='accounts'>
        <div class='account'>
          <div class='name'>Bank 1</div>
          <div class='balance'>$1</div>
          <div class='lastupdate'>Updated 1 week ago</div>
        </div>
      </div>
      <!-- Categories -->
    </template>
  </LayoutPaper>
</template>

<script setup>
  import LayoutPaper from '@/components/LayoutPaper.vue'
</script>

<style>
  #budgetsettings {
    .accounts {
      display: flex;
      flex-wrap: wrap;
      .account {
        width: 30%;
        height: 100px;
      }
    }
  }
</style>