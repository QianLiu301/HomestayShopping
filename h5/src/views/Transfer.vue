<template>
  <div class="page-container">
    <van-nav-bar :title="t('transfer.title')" left-arrow @click-left="$router.back()" />

    <div v-if="pageLoading" style="text-align: center; padding: 60px;">
      <van-loading size="24" />
    </div>

    <template v-else>
      <!-- Service type -->
      <div class="card">
        <div class="card-title">{{ t('transfer.title') }}</div>
        <van-radio-group v-model="form.service_type" direction="horizontal" class="service-radios">
          <van-radio name="pickup">{{ t('transfer.pickup') }}</van-radio>
          <van-radio name="dropoff">{{ t('transfer.dropoff') }}</van-radio>
          <van-radio name="combo">{{ t('transfer.combo') }}</van-radio>
        </van-radio-group>
        <div v-if="form.service_type === 'combo' && pricing" class="combo-tip">
          {{ t('transfer.comboDiscount', { discount: pricing.combo_discount * 100 }) }}
        </div>
      </div>

      <!-- Vehicle selection -->
      <div class="card">
        <div class="card-title">{{ t('transfer.selectVehicle') }}</div>
        <div class="vehicle-list">
          <div
            v-for="v in vehicles"
            :key="v.id"
            class="vehicle-card"
            :class="{ active: form.vehicle_id === v.id }"
            @click="form.vehicle_id = v.id"
          >
            <div class="vehicle-icon">
              <van-icon name="logistics" size="28" :color="form.vehicle_id === v.id ? '#1a73e8' : '#999'" />
            </div>
            <div class="vehicle-info">
              <div class="vehicle-name">{{ v.name }}</div>
              <div class="vehicle-desc">
                {{ t('transfer.seats', { n: v.seats }) }} · {{ t('transfer.luggage', { n: v.luggage_capacity }) }}
              </div>
            </div>
            <div class="vehicle-price">
              {{ v.extra_price > 0 ? t('transfer.extraPrice', { price: v.extra_price }) : t('transfer.noExtra') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Flight info -->
      <div class="card">
        <van-field
          v-model="form.flight_no"
          :label="t('transfer.flightNo')"
          :placeholder="t('transfer.flightNo')"
        />
        <van-field
          :label="t('transfer.flightTime')"
          :model-value="form.flight_time ? formatDate(form.flight_time) : ''"
          :placeholder="t('transfer.flightTime')"
          readonly
          is-link
          @click="showDatePicker = true"
        />
      </div>

      <!-- Address -->
      <div class="card">
        <div class="card-title">{{ t('transfer.selectAddress') }}</div>
        <van-radio-group v-model="addressType" class="address-radios">
          <van-radio name="homestay">{{ t('transfer.homestayAddress') }}</van-radio>
          <van-radio name="custom">{{ t('transfer.customAddress') }}</van-radio>
        </van-radio-group>

        <div v-if="addressType === 'homestay'" style="margin-top: 12px;">
          <van-field
            :model-value="selectedLocationName"
            :placeholder="t('transfer.selectAddress')"
            readonly
            is-link
            @click="showLocationPicker = true"
          />
        </div>

        <div v-else style="margin-top: 12px;">
          <van-field
            :model-value="form.custom_district"
            :placeholder="t('transfer.selectDistrict')"
            readonly
            is-link
            @click="showDistrictPicker = true"
          />
          <van-field
            v-model="form.custom_address"
            :placeholder="t('transfer.inputAddress')"
            type="textarea"
            rows="2"
            autosize
          />
        </div>
      </div>

      <!-- Contact info -->
      <div class="card">
        <div class="card-title">{{ t('transfer.contactInfo') }}</div>
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

      <!-- Price detail -->
      <div class="card">
        <div class="card-title">{{ t('transfer.priceDetail') }}</div>
        <div class="price-line">
          <span>{{ t('transfer.basePrice') }}</span>
          <span>¥{{ basePrice }}</span>
        </div>
        <div class="price-line">
          <span>{{ t('transfer.vehicleExtra') }}</span>
          <span>¥{{ vehicleExtra }}</span>
        </div>
        <div v-if="couponDiscount > 0" class="price-line discount">
          <span>{{ t('transfer.discount') }}</span>
          <span>-¥{{ couponDiscount }}</span>
        </div>
        <div class="price-line total">
          <span>{{ t('transfer.totalPrice') }}</span>
          <span class="total-amount">¥{{ totalPrice }}</span>
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

      <!-- Submit -->
      <div style="padding: 16px;">
        <van-button round block type="primary" size="large" :loading="submitting" @click="onSubmit">
          {{ t('transfer.submitOrder') }} ¥{{ totalPrice }}
        </van-button>
      </div>
      <div style="height: 20px;"></div>
    </template>

    <!-- Date picker popup -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        v-model="datePickerValue"
        :title="t('transfer.flightTime')"
        :min-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- Location picker popup -->
    <van-popup v-model:show="showLocationPicker" position="bottom" round>
      <van-picker
        :title="t('transfer.homestayAddress')"
        :columns="locationColumns"
        @confirm="onLocationConfirm"
        @cancel="showLocationPicker = false"
      />
    </van-popup>

    <!-- District picker popup -->
    <van-popup v-model:show="showDistrictPicker" position="bottom" round>
      <van-picker
        :title="t('transfer.selectDistrict')"
        :columns="districtColumns"
        @confirm="onDistrictConfirm"
        @cancel="showDistrictPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getVehicles, getLocations, getDistricts, getTransferPrice, createTransferOrder, verifyCoupon } from '../api'

const { t } = useI18n()
const router = useRouter()

const pageLoading = ref(true)
const submitting = ref(false)
const vehicles = ref([])
const locations = ref([])
const districts = ref([])
const pricing = ref(null)

const form = reactive({
  service_type: 'pickup',
  vehicle_id: null,
  flight_no: '',
  flight_time: null,
  location_id: null,
  custom_address: '',
  custom_district: '',
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

const showDatePicker = ref(false)
const showLocationPicker = ref(false)
const showDistrictPicker = ref(false)

const now = new Date()
const datePickerValue = ref([
  String(now.getFullYear()),
  String(now.getMonth() + 1).padStart(2, '0'),
  String(now.getDate()).padStart(2, '0')
])

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

const selectedVehicle = computed(() => vehicles.value.find(v => v.id === form.vehicle_id))

const basePrice = computed(() => {
  if (!pricing.value) return 0
  if (form.service_type === 'pickup') return pricing.value.pickup_price
  if (form.service_type === 'dropoff') return pricing.value.dropoff_price
  return pricing.value.combo_price
})

const vehicleExtra = computed(() => selectedVehicle.value?.extra_price || 0)

const totalPrice = computed(() =>
  Math.max(0, basePrice.value + vehicleExtra.value - couponDiscount.value)
)

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function onDateConfirm({ selectedValues }) {
  const [y, m, d] = selectedValues
  form.flight_time = `${y}-${m}-${d}T00:00:00`
  showDatePicker.value = false
}

function onLocationConfirm({ selectedOptions }) {
  const sel = selectedOptions[0]
  if (sel) {
    form.location_id = sel.value
  }
  showLocationPicker.value = false
}

function onDistrictConfirm({ selectedOptions }) {
  const sel = selectedOptions[0]
  if (sel) {
    form.custom_district = sel.value
  }
  showDistrictPicker.value = false
}

async function onVerifyCoupon() {
  if (!couponCode.value) return
  couponLoading.value = true
  try {
    const res = await verifyCoupon({
      code: couponCode.value,
      amount: basePrice.value + vehicleExtra.value,
      apply_to: 'transfer'
    })
    couponDiscount.value = res.data?.discount_amount || 0
  } catch (e) {
    couponDiscount.value = 0
    showToast(t('checkout.couponInvalid'))
  } finally {
    couponLoading.value = false
  }
}

async function onSubmit() {
  if (!form.vehicle_id) return showToast(t('transfer.selectVehicle'))
  if (!form.contact_name) return showToast(t('transfer.contactName'))
  if (!form.contact_phone && !form.contact_email) return showToast(t('checkout.phoneOrEmail'))

  const data = { ...form }
  if (addressType.value === 'homestay') {
    if (!form.location_id) return showToast(t('transfer.selectAddress'))
    delete data.custom_address
    delete data.custom_district
  } else {
    if (!form.custom_district) return showToast(t('transfer.selectDistrict'))
    if (!form.custom_address) return showToast(t('transfer.inputAddress'))
    delete data.location_id
  }

  if (couponCode.value && couponDiscount.value > 0) {
    data.coupon_code = couponCode.value
  }

  submitting.value = true
  try {
    const res = await createTransferOrder(data)
    router.replace({
      path: '/order-result',
      query: {
        orderNo: res.data.order_no,
        amount: res.data.total_price,
        type: 'transfer'
      }
    })
  } catch (e) {
    showToast(e.message)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const [vRes, lRes, dRes, pRes] = await Promise.all([
      getVehicles(),
      getLocations(),
      getDistricts(),
      getTransferPrice()
    ])
    vehicles.value = vRes.data || []
    locations.value = lRes.data || []
    districts.value = dRes.data || []
    pricing.value = pRes.data

    if (vehicles.value.length) {
      form.vehicle_id = vehicles.value[0].id
    }
  } catch (e) {
    console.error(e)
  } finally {
    pageLoading.value = false
  }
})
</script>

<style scoped>
.service-radios {
  gap: 12px;
}

.combo-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--accent);
  background: #fff7f0;
  padding: 6px 12px;
  border-radius: 6px;
}

.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vehicle-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.vehicle-card.active {
  border-color: var(--primary);
  background: var(--primary-light);
}

.vehicle-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vehicle-card.active .vehicle-icon {
  background: rgba(26, 115, 232, 0.1);
}

.vehicle-info {
  flex: 1;
}

.vehicle-name {
  font-size: 15px;
  font-weight: 600;
}

.vehicle-desc {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 2px;
}

.vehicle-price {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
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
