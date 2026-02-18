<template>
  <div class="page-container page-with-tabbar">
    <van-nav-bar :title="t('shop.title')" left-arrow @click-left="$router.back()">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <!-- Category tabs -->
    <van-tabs v-model:active="activeCategory" sticky shrink @change="onCategoryChange">
      <van-tab :title="t('common.all')" :name="0" />
      <van-tab
        v-for="cat in categories"
        :key="cat.id"
        :title="cat.name"
        :name="cat.id"
      />
    </van-tabs>

    <!-- Product list -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loadingMore"
        :finished="finished"
        :finished-text="products.length ? '' : ''"
        @load="loadMore"
      >
        <div class="product-grid" style="padding-top: 12px;">
          <div
            v-for="product in products"
            :key="product.id"
            class="product-card"
            @click="$router.push(`/product/${product.id}`)"
          >
            <img
              v-if="product.images?.length"
              :src="product.images[0]"
              :alt="product.name"
              class="product-image"
            />
            <div v-else class="placeholder-img">{{ product.name?.charAt(0) }}</div>
            <div class="product-info">
              <div class="product-name">{{ product.name }}</div>
              <div class="product-price">
                ¥{{ product.price }}
                <span v-if="product.original_price" class="original">¥{{ product.original_price }}</span>
              </div>
            </div>
          </div>
        </div>

        <van-empty v-if="!loadingMore && !products.length" :description="t('common.noData')" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getProducts, getCategories } from '../api'
import LangSwitch from '../components/LangSwitch.vue'

const { t } = useI18n()
const route = useRoute()

const categories = ref([])
const products = ref([])
const activeCategory = ref(Number(route.query.category) || 0)
const page = ref(1)
const loadingMore = ref(false)
const finished = ref(false)
const refreshing = ref(false)

onMounted(async () => {
  try {
    const res = await getCategories()
    categories.value = res.data || []
  } catch (e) {
    console.error(e)
  }
  loadMore()
})

async function loadMore() {
  try {
    const params = { page: page.value, per_page: 10 }
    if (activeCategory.value) {
      params.category_id = activeCategory.value
    }
    const res = await getProducts(params)
    const list = res.data?.list || []

    if (page.value === 1) {
      products.value = list
    } else {
      products.value.push(...list)
    }

    if (products.value.length >= (res.data?.total || 0)) {
      finished.value = true
    }
    page.value++
  } catch (e) {
    finished.value = true
  } finally {
    loadingMore.value = false
    refreshing.value = false
  }
}

function onCategoryChange() {
  page.value = 1
  finished.value = false
  products.value = []
  loadMore()
}

function onRefresh() {
  page.value = 1
  finished.value = false
  loadMore()
}
</script>
