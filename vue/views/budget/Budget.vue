<template>
  <div id='budget'>
    <LayoutSidePanel>
      <!-- Side Panel -->
      <template #panel>
        <div class='menu' style='margin-top: 30px;'>
          <div class='item'>
            <span class='icon'>account_balance</span>
            Transactions
          </div>
          <div class='subitem account'>
            <div class='name'>Bank 2 Balance</div>
            <div class='balance'>$1</div>
            <div class='lastupdate'>Updated 1 week ago</div>
          </div>
          <div class='subitem account'>
            <div class='name'>Bank 1 Balance</div>
            <div class='balance'>$2</div>
            <div class='lastupdate'>Updated 3 days ago</div>
          </div>
          <div class='item'>
            <span class='icon'>checkbook</span>
            Year Overview
          </div>
          <div class='subitem account'>
            <div class='name'>Total Spent 2025</div>
            <div class='balance'>$2</div>
            <div class='lastupdate'>Average $123 / month</div>
          </div>
          <div class='subitem account'>
            <div class='name'>Total Saved 2025</div>
            <div class='balance'>$2</div>
            <div class='lastupdate'>Average $124 / month</div>
          </div>
          <div class='item'>
            <span class='icon'>settings</span>
            Categories
          </div>
        </div>
      </template>
      <!-- Content -->
      <template #content>
        <LayoutPaper width='1200'>
          <template #content>
            Hello Content!
          </template>
        </LayoutPaper>
      </template>
    </LayoutSidePanel>
  </div>
</template>

<script setup>
  import {inject, onBeforeMount} from 'vue'
  import {utils} from '@/utils'
  import LayoutPaper from '@/components/LayoutPaper.vue'
  import LayoutSidePanel from '@/components/LayoutSidePanel.vue'

  onBeforeMount(function() { utils.setNavPosition('top') })
</script>

<style>
  #budget {
    .sidepanel-panel .menu {
      color: var(--linkcolor);
      .item {
        margin-top: 20px;
        padding: 7px 20px 10px 20px;
        font-size: 16px;
        border-left: 3px solid transparent;
        cursor: pointer;
        overflow: hidden;
        text-overflow: ellipsis;
        user-select: none;
        white-space: nowrap;
        transition: all 0.3s ease;
        border-bottom: 0px solid #0000;
        &:hover, &:focus, &.selected {
          color: var(--fgcolor);
          border-left: 3px solid var(--accent);
          background-color: #fff1;
        }
      }
      .subitem {
        padding: 3px 20px 3px 60px;
        font-size: 12px;
        opacity: 0.6;
        .name { float: left; }
        .balance { text-align: right; }
        .lastupdate { font-size: 9px; opacity: 0.6;}
      }
      .icon {
        font-size: 22px;
        position: relative;
        top: 5px;
        margin-right: 10px;
      }
    }
  }
</style>