<!--
页面左下角圆圈问号：点击跳出弹窗，不同页面有不同hints
-->

<template>
  <div
    v-if="hasHint"
    class="help-hint"
    @mouseleave="open = false"
  >
    <button type="button" class="trigger" @click.stop="toggle">?</button>
    <transition name="fade">
      <div v-if="open" class="panel">
        <slot>{{ hints }}</slot>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

const props = defineProps<{ hints?: string }>();
const open = ref(false);
const hasHint = computed(() => Boolean(props.hints?.trim().length));
const hints = computed(() => props.hints?.trim() ?? '');

function toggle() {
  open.value = !open.value;
}
</script>

<style scoped>
.help-hint {
  position: fixed;
  bottom: 24px;
  left: 24px;
  z-index: 999;
  width: 36px;
  height: 36px;
}

.trigger {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #222;
  background: #fff;
  color: #222;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.trigger:hover,
.trigger:focus {
  background: #222;
  color: #fff;
}

.panel {
  position: absolute;
  left: calc(100% + 12px);
  bottom: calc(100% + 12px);
  padding: 12px 16px;
  border: 1px solid #222;
  background: #fff;
  color: #222;
  min-width: 220px;
  max-width: 280px;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  pointer-events: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
