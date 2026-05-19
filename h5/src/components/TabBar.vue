<template>
  <van-tabbar v-model="active" :placeholder="true" route>
    <van-tabbar-item name="Home" to="/" icon="home-o">{{ t('common.home') }}</van-tabbar-item>
    <van-tabbar-item name="Shop" to="/shop" icon="shop-o">{{ t('common.shop') }}</van-tabbar-item>
    <van-tabbar-item name="Tickets" to="/tickets" icon="coupon-o">{{ t('tickets.title') }}</van-tabbar-item>
    <van-tabbar-item name="Cart" to="/cart" icon="cart-o" :badge="cartCount || ''">{{ t('common.cart') }}</van-tabbar-item>
    <van-tabbar-item name="OrderQuery" to="/order-query" icon="description">{{ t('common.orders') }}</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '../stores/cart'

const { t } = useI18n()
const route = useRoute()
const cart = useCartStore()

function resolveTabName(name) {
  if (['Tickets', 'TicketDetail', 'TicketCheckout', 'TicketOrderResult', 'TicketOrderQuery'].includes(name)) {
    return 'Tickets'
  }
  return name || 'Home'
}

const active = ref(resolveTabName(route.name))
const cartCount = computed(() => cart.totalCount > 0 ? cart.totalCount : undefined)

watch(() => route.name, (name) => {
  active.value = resolveTabName(name)
})
</script>
