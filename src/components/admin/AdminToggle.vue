<script setup>
// A compact, luxury toggle switch for the Admin Panel forms. Uses v-model and is
// fully logical/RTL-aware — the knob travels along the inline axis, so it flips
// automatically under dir="rtl". Colours come from the shared theme tokens.
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  label: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
const toggle = () => { if (!props.disabled) emit('update:modelValue', !props.modelValue) }
</script>

<template>
  <button
    type="button"
    role="switch"
    :aria-checked="modelValue"
    :aria-label="label || undefined"
    :disabled="disabled"
    @click="toggle"
    class="admin-switch"
    :class="{ 'is-on': modelValue, 'is-disabled': disabled }"
  >
    <span class="admin-switch-track" aria-hidden="true">
      <span class="admin-switch-knob"></span>
    </span>
    <span v-if="label" class="admin-switch-label">{{ label }}</span>
  </button>
</template>

<style scoped>
.admin-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
}
.admin-switch.is-disabled { cursor: not-allowed; opacity: 0.55; }
.admin-switch-track {
  position: relative;
  width: 42px;
  height: 24px;
  border-radius: 999px;
  background: rgb(var(--c-parchment-deep));
  box-shadow: inset 1px 1px 3px rgb(2 6 12 / 0.18);
  transition: background 260ms ease;
  flex-shrink: 0;
}
.admin-switch.is-on .admin-switch-track {
  background: linear-gradient(135deg, rgb(var(--c-gold-light)), rgb(var(--c-gold)));
}
.admin-switch-knob {
  position: absolute;
  top: 3px;
  inset-inline-start: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgb(var(--c-parchment-light));
  box-shadow: 0 2px 5px rgb(2 6 12 / 0.3);
  transition: inset-inline-start 260ms cubic-bezier(0.16, 1, 0.3, 1);
}
.admin-switch.is-on .admin-switch-knob { inset-inline-start: 21px; }
.admin-switch-label {
  font-size: 0.8rem;
  font-weight: 300;
  color: rgb(var(--c-ink-soft));
}
</style>
