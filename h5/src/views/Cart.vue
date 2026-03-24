<template>
  <div class="page-container page-with-tabbar">
    <van-nav-bar :title="t('cart.title')" />

    <div v-if="!cart.items.length" class="empty-cart">
      <van-empty :description="t('cart.empty')">
        <van-button round type="primary" size="small" @click="$router.push('/shop')">
          {{ t('cart.goShop') }}
        </van-button>
      </van-empty>
    </div>

    <template v-else>
      <van-swipe-cell v-for="item in cart.items" :key="item.key">
        <div class="cart-item" @click="$router.push(`/product/${item.productId}`)">
          <img v-if="item.image" :src="$resolveUrl(item.image)" class="cart-img" />
          <div v-else class="cart-img placeholder">{{ item.name?.charAt(0) }}</div>
          <div class="cart-info">
            <div class="cart-name">{{ item.name }}</div>
            <div v-if="item.specName" class="cart-spec">{{ item.specName }}</div>
            <div class="cart-bottom">
              <span class="cart-price">¥{{ item.price }}</span>
              <van-stepper
                :model-value="item.quantity"
                min="1"
                max="99"
                theme="round"
                @change="(v) => cart.updateQuantity(item.key, v)"
                @click.stop
              />
            </div>
          </div>
        </div>
        <template #right>
          <van-button square type="danger" :text="t('cart.delete')" class="delete-btn" @click="cart.removeItem(item.key)" />
        </template>
      </van-swipe-cell>

      <div style="height: 70px;"></div>

      <van-submit-bar
        :price="cart.totalPrice * 100"
        :button-text="t('cart.checkout')"
        :label="t('cart.total') + '：'"
        currency="¥"
        @submit="$router.push('/checkout')"
      >
        <template #tip>
          {{ t('cart.selected', { count: cart.totalCount }) }}
        </template>
      </van-submit-bar>
    </template>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useCartStore } from '../stores/cart'

const { t } = useI18n()
const cart = useCartStore()
</script>

<style scoped>
.empty-cart {
  padding-top: 80px;
}

.cart-item {
  display: flex;
  padding: 12px 16px;
  background: var(--white);
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid var(--border);
}

.cart-img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.cart-img.placeholder {
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-light);
}

.cart-info {
  flex: 1;
  min-width: 0;
}

.cart-name {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cart-spec {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 4px;
  background: #f5f5f5;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
}

.cart-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.cart-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--accent);
}

.delete-btn {
  height: 100%;
}

:deep(.van-submit-bar) {
  bottom: 50px;
}
</style>
