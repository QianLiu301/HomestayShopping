import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref(JSON.parse(localStorage.getItem('cart') || '[]'))

  const totalCount = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))
  const totalPrice = computed(() => items.value.reduce((sum, item) => sum + item.price * item.quantity, 0))

  function save() {
    localStorage.setItem('cart', JSON.stringify(items.value))
  }

  function addItem(product, spec = null) {
    const key = `${product.id}_${spec?.name || ''}`
    const existing = items.value.find(i => i.key === key)

    if (existing) {
      existing.quantity++
    } else {
      items.value.push({
        key,
        productId: product.id,
        name: product.name,
        image: product.images?.[0] || '',
        price: spec?.price ?? product.price,
        specName: spec?.name || null,
        quantity: 1
      })
    }
    save()
  }

  function updateQuantity(key, quantity) {
    const item = items.value.find(i => i.key === key)
    if (item) {
      if (quantity <= 0) {
        items.value = items.value.filter(i => i.key !== key)
      } else {
        item.quantity = quantity
      }
      save()
    }
  }

  function removeItem(key) {
    items.value = items.value.filter(i => i.key !== key)
    save()
  }

  function clear() {
    items.value = []
    save()
  }

  return { items, totalCount, totalPrice, addItem, updateQuantity, removeItem, clear }
})
