<template>
  <div class="page-container">
    <van-nav-bar :title="t('checkout.title')" left-arrow @click-left="$router.back()" />

    <div v-if="pageLoading" style="text-align: center; padding: 60px;">
      <van-loading size="24" />
    </div>

    <template v-else>
      <!-- Order items summary -->
      <div class="card">
        <div class="card-title">{{ t('checkout.orderItems') }} ({{ cart.totalCount }})</div>
        <div class="order-items">
          <div v-for="item in cart.items" :key="item.key" class="checkout-item">
            <img v-if="item.image" :src="item.image" class="item-img" />
            <div v-else class="item-img placeholder">{{ item.name?.charAt(0) }}</div>
            <div class="item-info">
              <div class="item-name">{{ item.name }}</div>
              <div v-if="item.specName" class="item-spec">{{ item.specName }}</div>
              <div class="item-bottom">
                <span class="item-price">¥{{ item.price }}</span>
                <span class="item-qty">x{{ item.quantity }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Address -->
      <div class="card">
        <div class="card-title">{{ t('checkout.address') }}</div>
        <van-radio-group v-model="addressType" class="address-radios">
          <van-radio name="homestay">{{ t('transfer.homestayAddress') }}</van-radio>
          <van-radio name="custom">{{ t('transfer.customAddress') }}</van-radio>
        </van-radio-group>

        <div v-if="addressType === 'homestay'" style="margin-top: 12px;">
          <van-field
            :model-value="selectedLocationName"
            :placeholder="t('checkout.selectLocation')"
            readonly
            is-link
            required
            @click="showLocationPicker = true"
          />
          <van-field
            v-model="form.room_number"
            :label="t('checkout.roomNumber')"
            :placeholder="t('checkout.roomPlaceholder')"
            required
          />
        </div>

        <div v-else style="margin-top: 12px;">
          <van-field
            :model-value="form.custom_district"
            :placeholder="t('transfer.selectDistrict')"
            readonly
            is-link
            required
            @click="showDistrictPicker = true"
          />
          <van-field
            v-model="form.custom_address"
            :placeholder="t('transfer.inputAddress')"
            type="textarea"
            rows="2"
            autosize
            required
          />
          <van-field
            v-model="form.room_number"
            :label="t('checkout.roomNumber')"
            :placeholder="t('checkout.roomPlaceholder')"
            required
          />
        </div>
      </div>

      <!-- Contact -->
      <div class="card">
        <div class="card-title">{{ t('checkout.contact') }}</div>
        <van-field v-model="form.contact_name" :label="t('transfer.contactName')" :placeholder="t('transfer.contactName')" required />
        <van-field v-model="form.contact_phone" :label="t('transfer.contactPhone')" :placeholder="t('transfer.contactPhone')" type="tel" />
        <van-field v-model="form.contact_email" :label="t('transfer.contactEmail')" :placeholder="t('transfer.contactEmail')" type="email" />
        <van-field v-model="form.remark" :label="t('transfer.remark')" :placeholder="t('transfer.remarkPlaceholder')" type="textarea" rows="2" autosize />
      </div>

      <!-- Coupon -->
      <div class="card">
        <div class="card-title">{{ t('checkout.coupon') }}</div>
        <div class="coupon-row">
          <van-field v-model="couponCode" :placeholder="t('checkout.couponPlaceholder')" style="flex:1" />
          <van-button size="small" type="primary" :loading="couponLoading" @click="onVerifyCoupon">{{ t('checkout.verify') }}</van-button>
        </div>
        <div v-if="couponDiscount > 0" class="coupon-msg success">
          {{ t('checkout.couponValid', { amount: couponDiscount }) }}
        </div>
      </div>

      <!-- Payment -->
      <div class="card">
        <div class="card-title">{{ t('checkout.payment') }}</div>
        <van-radio-group v-model="form.payment_method">
          <van-cell-group :border="false">
            <van-cell :title="t('checkout.wechat')" clickable @click="form.payment_method = 'wechat'">
              <template #right-icon><van-radio name="wechat" /></template>
            </van-cell>
            <van-cell :title="t('checkout.alipay')" clickable @click="form.payment_method = 'alipay'">
              <template #right-icon><van-radio name="alipay" /></template>
            </van-cell>
            <van-cell :title="t('checkout.creditCard')" clickable @click="form.payment_method = 'credit_card'">
              <template #right-icon><van-radio name="credit_card" /></template>
            </van-cell>
          </van-cell-group>
        </van-radio-group>
      </div>

      <!-- Price summary -->
      <div class="card">
        <div class="price-line">
          <span>{{ t('checkout.subtotal') }}</span>
          <span>¥{{ cart.totalPrice.toFixed(2) }}</span>
        </div>
        <div v-if="couponDiscount > 0" class="price-line discount">
          <span>{{ t('transfer.discount') }}</span>
          <span>-¥{{ couponDiscount }}</span>
        </div>
        <div class="price-line total">
          <span>{{ t('checkout.totalPrice') }}</span>
          <span class="total-amount">¥{{ finalPrice }}</span>
        </div>
      </div>

      <!-- Submit -->
      <div style="padding: 16px;">
        <van-button round block type="danger" size="large" :loading="submitting" @click="onSubmit">
          {{ t('checkout.placeOrder') }} ¥{{ finalPrice }}
        </van-button>
      </div>
      <div style="height: 20px;"></div>
    </template>

    <!-- Location picker -->
    <van-popup v-model:show="showLocationPicker" position="bottom" round>
      <van-picker
        :title="t('checkout.selectLocation')"
        :columns="locationColumns"
        @confirm="onLocationConfirm"
        @cancel="showLocationPicker = false"
      />
    </van-popup>

    <!-- District picker -->
    <van-popup v-model:show="showDistrictPicker" position="bottom" round>
      <van-picker
        :title="t('transfer.selectDistrict')"
        :columns="districtColumns"
        @confirm="onDistrictConfirm"
        @cancel="showDistrictPicker = false"
      />
    </van-popup>

    <!-- Payment QR popup (v-if ensures overlay is not in DOM until needed) -->
    <PaymentPopup
      v-if="showPaymentPopup"
      v-model:show="showPaymentPopup"
      :method="form.payment_method"
      :amount="finalPrice"
      :order-no="pendingOrderNo"
      @paid="onPaymentConfirmed"
      @cancel="onPaymentCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getLocations, getDistricts, createShopOrder, verifyCoupon } from '../api'
import { useCartStore } from '../stores/cart'
import PaymentPopup from '../components/PaymentPopup.vue'

const { t } = useI18n()
const router = useRouter()
const cart = useCartStore()

const pageLoading = ref(true)
const submitting = ref(false)
const locations = ref([])
const districts = ref([])

const form = reactive({
  location_id: null,
  custom_address: '',
  custom_district: '',
  room_number: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  remark: '',
  payment_method: 'wechat'
})

const addressType = ref('homestay')
const couponCode = ref('')
const couponDiscount = ref(0)
const couponLoading = ref(false)

const showLocationPicker = ref(false)
const showDistrictPicker = ref(false)
const showPaymentPopup = ref(false)
const pendingOrderNo = ref('')
const pendingAmount = ref('')

const locationColumns = computed(() =>
  locations.value.map(l => ({ text: l.name, value: l.id }))
)

const districtColumns = computed(() =>
  districts.value.map(d => ({ text: d.label, value: d.value }))
)

const selectedLocationName = computed(() => {
  if (!form.location_id) return ''
  return locations.value.find(l => l.id === form.location_id)?.name || ''
})

const finalPrice = computed(() =>
  Math.max(0, cart.totalPrice - couponDiscount.value).toFixed(2)
)

function onLocationConfirm({ selectedOptions }) {
  const sel = selectedOptions[0]
  if (sel) form.location_id = sel.value
  showLocationPicker.value = false
}

function onDistrictConfirm({ selectedOptions }) {
  const sel = selectedOptions[0]
  if (sel) form.custom_district = sel.value
  showDistrictPicker.value = false
}

async function onVerifyCoupon() {
  if (!couponCode.value) return
  couponLoading.value = true
  try {
    const res = await verifyCoupon({
      code: couponCode.value,
      amount: cart.totalPrice,
      apply_to: 'shop'
    })
    couponDiscount.value = res.data?.discount_amount || 0
  } catch (e) {
    couponDiscount.value = 0
    showToast(t('checkout.couponInvalid'))
  } finally {
    couponLoading.value = false
  }
}

function validationFail(msg) {
  console.warn('Validation failed:', msg)
  showToast({ message: msg, position: 'top', duration: 3000 })
  // Scroll to top so user can see which field is missing
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function onSubmit() {
  console.log('onSubmit called', { addressType: addressType.value, form: JSON.parse(JSON.stringify(form)), cartItems: cart.items.length })
  try {
    // Validate address
    if (addressType.value === 'homestay') {
      if (!form.location_id) { validationFail(t('checkout.selectLocation')); return }
    } else {
      if (!form.custom_district) { validationFail(t('transfer.selectDistrict')); return }
      if (!form.custom_address) { validationFail(t('transfer.inputAddress')); return }
    }

    // Room number is required
    if (!form.room_number) { validationFail(t('checkout.roomRequired')); return }

    // Validate contact info
    if (!form.contact_name) { validationFail(t('transfer.contactName')); return }
    if (!form.contact_phone && !form.contact_email) { validationFail(t('checkout.phoneOrEmail')); return }

    const data = {
      contact_name: form.contact_name,
      contact_phone: form.contact_phone,
      contact_email: form.contact_email,
      room_number: form.room_number,
      remark: form.remark,
      payment_method: form.payment_method,
      items: cart.items.map(item => ({
        product_id: item.productId,
        quantity: item.quantity,
        spec_name: item.specName || undefined
      }))
    }

    if (addressType.value === 'homestay') {
      data.location_id = form.location_id
    } else {
      data.custom_address = form.custom_address
      data.custom_district = form.custom_district
    }

    if (couponCode.value && couponDiscount.value > 0) {
      data.coupon_code = couponCode.value
    }

    submitting.value = true
    const res = await createShopOrder(data)
    cart.clear()
    pendingOrderNo.value = res.data?.order_no || res.order_no || ''
    pendingAmount.value = res.data?.total_price || res.total_price || ''

    // For wechat/alipay show QR payment popup; for credit_card go directly to result
    if (form.payment_method === 'wechat' || form.payment_method === 'alipay') {
      showPaymentPopup.value = true
    } else {
      goToResult()
    }
  } catch (e) {
    console.error('Submit order error:', e)
    showToast(e.message || String(e))
  } finally {
    submitting.value = false
  }
}

function goToResult() {
  router.replace({
    path: '/order-result',
    query: {
      orderNo: pendingOrderNo.value,
      amount: pendingAmount.value,
      type: 'shop'
    }
  })
}

function onPaymentConfirmed() {
  showToast(t('payment.paymentSubmitted'))
  goToResult()
}

function onPaymentCancel() {
  // Order already created, still go to result page
  goToResult()
}

onMounted(async () => {
  if (!cart.items.length) {
    router.replace('/cart')
    return
  }
  try {
    const [lRes, dRes] = await Promise.all([getLocations(), getDistricts()])
    locations.value = lRes.data || []
    districts.value = dRes.data || []
  } catch (e) {
    console.error(e)
  } finally {
    pageLoading.value = false
  }
})
</script>

<style scoped>
.order-items {
  max-height: 200px;
  overflow-y: auto;
}

.checkout-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.checkout-item:last-child {
  border-bottom: none;
}

.item-img {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.item-img.placeholder {
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--text-light);
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 13px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-spec {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 2px;
}

.item-bottom {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
}

.item-price {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
}

.item-qty {
  font-size: 13px;
  color: var(--text-light);
}

.address-radios {
  display: flex;
  gap: 16px;
}

.coupon-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.coupon-msg.success {
  margin-top: 8px;
  font-size: 13px;
  color: var(--success);
}

.price-line {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.price-line.discount {
  color: var(--success);
}

.price-line.total {
  border-top: 1px solid var(--border);
  margin-top: 4px;
  padding-top: 12px;
  font-weight: 600;
  color: var(--text);
}

.total-amount {
  font-size: 20px;
  color: var(--accent);
}
</style>
