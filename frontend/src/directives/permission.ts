import type { App, DirectiveBinding } from 'vue';
import { useUserStore } from '@/store/useUserStore';

type Roles = 'admin' | 'sc' | 'tutor';
type Checker = (ctx: { role?: Roles; isAuthenticated: boolean }) => boolean;
type BindingVal = Roles | Roles[] | Checker;

function check(val: BindingVal, role?: Roles, isAuthenticated?: boolean): boolean {
  if (typeof val === 'function') {
    return val({ role, isAuthenticated: !!isAuthenticated });
  }
  if (Array.isArray(val)) {
    return !!role && val.includes(role);
  }
  return !!role && role === val;
}

function apply(el: HTMLElement, binding: DirectiveBinding<BindingVal>) {
  const store = useUserStore();
  const ok = check(binding.value, store.role as Roles, store.isAuthenticated);
  if (!ok) {
    el.parentNode && el.parentNode.removeChild(el);
  }
}

export default {
  install(app: App) {
    app.directive('permission', {
      mounted: apply,
      updated: apply
    });
  }
};
