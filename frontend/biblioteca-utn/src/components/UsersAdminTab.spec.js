import { mount } from '@vue/test-utils'
import { expect, test } from 'vitest'
import { createPinia } from 'pinia'
import TicketsAdminTab from './TicketsAdminTab.vue'

test('renderiza el componente TicketsAdminTab correctamente', () => {
  const wrapper = mount(TicketsAdminTab, {
    global: {
      plugins: [createPinia()]
    }
  })
  
  expect(wrapper.exists()).toBe(true)
})