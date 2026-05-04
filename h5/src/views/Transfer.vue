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
        <div class="entry-discount-banner" :class="{ active: form.service_type === 'combo' }">
          <div class="entry-discount-badge">90%</div>
          <div class="entry-discount-text">{{ t('transfer.comboPromoBanner') }}</div>
        </div>
        <van-radio-group v-model="form.service_type" direction="horizontal" class="service-radios">
          <van-radio name="pickup">{{ t('transfer.pickup') }}</van-radio>
          <van-radio name="dropoff">{{ t('transfer.dropoff') }}</van-radio>
          <van-radio name="combo">{{ t('transfer.combo') }}</van-radio>
        </van-radio-group>
        <div v-if="form.service_type === 'combo'" class="combo-tip">
          <div class="combo-tip-title">{{ t('transfer.combo') }}</div>
          <div class="combo-tip-desc">{{ t('transfer.comboPriceTip', { combo: vehicleServicePrice(selectedVehicle, 'combo') }) }}</div>
        </div>
        <div v-else-if="servicePriceTip" class="combo-tip service-tip">
          {{ servicePriceTip }}
        </div>
      </div>

      <!-- Vehicle selection -->
      <div class="card">
        <div class="card-title">{{ t('transfer.selectVehicle') }} <span class="required">*</span></div>
        <div class="vehicle-intro">
          <div class="vehicle-intro-title">{{ t('transfer.featuredVehicles') }}</div>
          <div class="vehicle-intro-desc">{{ t('transfer.featuredVehiclesDesc') }}</div>
        </div>

        <div class="vehicle-list">
          <button
            v-for="v in vehicles"
            :key="v.id"
            type="button"
            class="vehicle-card"
            :class="{ active: form.vehicle_id === v.id }"
            @click="selectVehicle(v.id)"
          >
            <div class="vehicle-icon">
              <img
                v-if="vehiclePrimaryImage(v)"
                :src="$resolveUrl(vehiclePrimaryImage(v))"
                :alt="vehicleDisplayName(v)"
                class="vehicle-img"
                @click.stop="previewVehicle(v)"
              />
              <van-icon v-else name="logistics" size="28" :color="form.vehicle_id === v.id ? '#1a73e8' : '#999'" />
              <div v-if="(v.images?.length || 0) > 1" class="vehicle-image-badge">{{ v.images.length }}</div>
            </div>
            <div class="vehicle-info">
              <div class="vehicle-name-row">
                <div class="vehicle-name">{{ vehicleDisplayName(v) }}</div>
                <span class="vehicle-state-tag">{{ form.vehicle_id === v.id ? t('transfer.selectedVehicle') : t('transfer.recommendedVehicle') }}</span>
              </div>
              <div v-if="v.model" class="vehicle-model">{{ t('transfer.vehicleModel') }}：{{ v.model }}</div>
              <div class="vehicle-highlights">
                <span class="vehicle-highlight-chip">{{ t('transfer.seats', { n: v.seats }) }}</span>
                <span v-if="vehicleCapacityText(v)" class="vehicle-highlight-chip">{{ vehicleCapacityText(v) }}</span>
                <span class="vehicle-highlight-chip">{{ vehiclePriceLabel(v) }}</span>
              </div>
              <div class="vehicle-desc">{{ t('transfer.vehicleGalleryHint') }}</div>
            </div>
            <div class="vehicle-side">
              <div class="vehicle-price-label">{{ t('transfer.approxPrice') }}</div>
              <div class="vehicle-price">{{ vehiclePriceLabel(v) }}</div>
              <div class="vehicle-side-tip">{{ t('transfer.tapToPreview') }}</div>
            </div>
          </button>
        </div>
      </div>

      <!-- ============ PICKUP SECTION ============ -->
      <div v-if="form.service_type === 'pickup' || form.service_type === 'combo'" class="card">
        <div class="card-title section-title pickup-title">
          <van-icon name="guide-o" size="18" />
          {{ t('transfer.pickupInfo') }}
        </div>

        <!-- Airport selection -->
        <div class="field-label">{{ t('transfer.selectAirport') }} <span class="required">*</span></div>
        <van-radio-group v-model="form.pickup_airport" direction="horizontal" class="airport-radios">
          <van-radio name="PVG">
            <div class="airport-label">{{ t('transfer.pudongAirport') }} <span class="airport-code">PVG</span></div>
          </van-radio>
          <van-radio name="SHA">
            <div class="airport-label">{{ t('transfer.hongqiaoAirport') }} <span class="airport-code">SHA</span></div>
          </van-radio>
        </van-radio-group>

        <!-- Flight info -->
        <van-field
          v-model="form.flight_no"
          :label="t('transfer.flightNo')"
          :placeholder="t('transfer.flightNoPlaceholder')"
          required
        />
        <van-field
          :label="t('transfer.flightTime')"
          :model-value="form.flight_time ? formatDate(form.flight_time) : ''"
          :placeholder="t('transfer.flightTime')"
          readonly
          is-link
          @click="activeDatePicker = 'pickup'; showDatePicker = true"
        />

        <!-- Route display -->
        <div class="route-display" v-if="form.pickup_airport">
          <div class="route-point from">
            <van-icon name="location-o" color="#1a73e8" />
            <span>{{ airportName(form.pickup_airport) }}</span>
          </div>
          <div class="route-arrow">→</div>
          <div class="route-point to">
            <van-icon name="wap-home-o" color="#8b6f47" />
            <span>{{ t('transfer.homestayDestination') }}</span>
          </div>
        </div>
      </div>

      <!-- ============ DROPOFF SECTION ============ -->
      <div v-if="form.service_type === 'dropoff' || form.service_type === 'combo'" class="card">
        <div class="card-title section-title dropoff-title">
          <van-icon name="logistics" size="18" />
          {{ t('transfer.dropoffInfo') }}
        </div>

        <!-- Airport selection -->
        <div class="field-label">{{ t('transfer.selectAirport') }} <span class="required">*</span></div>
        <van-radio-group v-model="dropoffAirport" direction="horizontal" class="airport-radios">
          <van-radio name="PVG">
            <div class="airport-label">{{ t('transfer.pudongAirport') }} <span class="airport-code">PVG</span></div>
          </van-radio>
          <van-radio name="SHA">
            <div class="airport-label">{{ t('transfer.hongqiaoAirport') }} <span class="airport-code">SHA</span></div>
          </van-radio>
        </van-radio-group>

        <!-- Flight info -->
        <van-field
          v-model="dropoffFlightNo"
          :label="t('transfer.flightNo')"
          :placeholder="t('transfer.flightNoPlaceholder')"
          required
        />
        <van-field
          :label="t('transfer.flightTime')"
          :model-value="dropoffFlightTime ? formatDate(dropoffFlightTime) : ''"
          :placeholder="t('transfer.flightTime')"
          readonly
          is-link
          @click="activeDatePicker = 'dropoff'; showDatePicker = true"
        />

        <!-- Route display -->
        <div class="route-display" v-if="dropoffAirport">
          <div class="route-point from">
            <van-icon name="wap-home-o" color="#8b6f47" />
            <span>{{ t('transfer.homestayDestination') }}</span>
          </div>
          <div class="route-arrow">→</div>
          <div class="route-point to">
            <van-icon name="location-o" color="#1a73e8" />
            <span>{{ airportName(dropoffAirport) }}</span>
          </div>
        </div>
      </div>

      <!-- ============ BOOKING NUMBER ============ -->
      <div class="card">
        <div class="card-title">{{ t('transfer.bookingNo') }} <span class="required">*</span></div>
        <van-field
          v-model="form.booking_no"
          :placeholder="t('transfer.bookingNoPlaceholder')"
        />
        <div class="booking-tip">{{ t('transfer.bookingNoTip') }}</div>
      </div>

      <!-- Contact info -->
      <div class="card">
        <div class="card-title">{{ t('transfer.contactInfo') }}</div>
        <van-field v-model="form.contact_name" :label="t('transfer.contactName')" :placeholder="t('transfer.contactName')" required />
        <van-field v-model="form.contact_phone" :label="t('transfer.contactPhone')" :placeholder="t('transfer.contactPhone')" type="tel">
          <template #label>
            <span>{{ t('transfer.contactPhone') }}</span>
            <span class="field-hint">{{ t('transfer.phoneOrEmailHint') }}</span>
          </template>
        </van-field>
        <van-field v-model="form.contact_email" :label="t('transfer.contactEmail')" :placeholder="t('transfer.contactEmail')" type="email">
          <template #label>
            <span>{{ t('transfer.contactEmail') }}</span>
            <span class="field-hint">{{ t('transfer.phoneOrEmailHint') }}</span>
          </template>
        </van-field>
        <van-field v-model="form.remark" :label="t('transfer.remark')" :placeholder="t('transfer.remarkPlaceholder')" type="textarea" rows="2" autosize />
      </div>

      <!-- Price detail -->
      <div class="card">
        <div class="card-title">{{ t('transfer.priceDetail') }}</div>
        <div class="price-line">
          <span>{{ t('transfer.selectedServicePrice') }}</span>
          <span>¥{{ basePrice }}</span>
        </div>
        <div class="price-line total">
          <span>{{ t('transfer.totalPrice') }}</span>
          <span class="total-amount">¥{{ totalPrice }}</span>
        </div>
      </div>

      <!-- Agree to terms -->
      <div class="card agree-card">
        <van-checkbox v-model="agreeTerms" icon-size="16">
          <span class="agree-text">
            {{ t('legal.agreePrefix') }}
            <router-link to="/privacy" class="agree-link">{{ t('legal.privacyPolicy') }}</router-link>
            {{ t('legal.agreeAnd') }}
            <router-link to="/terms" class="agree-link">{{ t('legal.termsOfService') }}</router-link>
          </span>
        </van-checkbox>
      </div>

      <!-- Validation error banner -->
      <div v-if="errorMsg" class="error-banner">
        <van-icon name="warning-o" size="18" />
        <span>{{ errorMsg }}</span>
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

    <van-popup v-model:show="showImagePreview" class="image-preview-popup" closeable>
      <div
        class="image-preview-wrapper"
        @click="showImagePreview = false"
        @touchstart.stop="onPreviewTouchStart"
        @touchend.stop="onPreviewTouchEnd"
      >
        <button
          v-if="previewImages.length > 1"
          type="button"
          class="image-nav image-nav-prev"
          @click.stop="showPrevPreview"
          aria-label="Previous image"
        >
          ‹
        </button>
        <img
          v-if="previewImage"
          :src="previewImage"
          :alt="previewTitle"
          class="image-preview-img"
          @click.stop
        />
        <button
          v-if="previewImages.length > 1"
          type="button"
          class="image-nav image-nav-next"
          @click.stop="showNextPreview"
          aria-label="Next image"
        >
          ›
        </button>
        <div v-if="previewTitle" class="image-preview-title">
          {{ previewTitle }}
          <span v-if="previewImages.length > 1" class="image-preview-count">{{ previewIndex + 1 }} / {{ previewImages.length }}</span>
        </div>
        <div v-if="previewImages.length > 1" class="image-preview-thumbs" @click.stop>
          <button
            v-for="(img, index) in previewImages"
            :key="`${img}-${index}`"
            type="button"
            class="image-preview-thumb"
            :class="{ active: index === previewIndex }"
            @click="setPreviewIndex(index)"
          >
            <img :src="img" :alt="`${previewTitle}-${index + 1}`" />
          </button>
        </div>
      </div>
    </van-popup>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getVehicles, createTransferOrder, resolveUrl } from '../api'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const pageLoading = ref(true)
const submitting = ref(false)
const errorMsg = ref('')
const vehicles = ref([])

const form = reactive({
  service_type: route.query.service_type || 'pickup',
  vehicle_id: null,
  pickup_airport: 'PVG',
  flight_no: '',
  flight_time: null,
  booking_no: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  remark: ''
})

// Dropoff fields (separate for combo, shared for single dropoff)
const dropoffAirport = ref('PVG')
const dropoffFlightNo = ref('')
const dropoffFlightTime = ref(null)

const showDatePicker = ref(false)
const activeDatePicker = ref('pickup') // 'pickup' or 'dropoff'
const pendingOrderNo = ref('')
const pendingAmount = ref('')
const agreeTerms = ref(false)
const showImagePreview = ref(false)
const previewImage = ref('')
const previewTitle = ref('')
const previewImages = ref([])
const previewIndex = ref(0)
const previewTouchStartX = ref(0)
const previewTouchStartY = ref(0)

const now = new Date()
const datePickerValue = ref([
  String(now.getFullYear()),
  String(now.getMonth() + 1).padStart(2, '0'),
  String(now.getDate()).padStart(2, '0')
])

const selectedVehicle = computed(() => vehicles.value.find(v => v.id === form.vehicle_id))

function selectVehicle(vehicleId) {
  form.vehicle_id = vehicleId
}

function vehicleDisplayName(vehicle) {
  if (!vehicle) return ''
  return vehicle.name || vehicle.model || ''
}

function vehicleServicePrice(vehicle, serviceType = form.service_type) {
  if (!vehicle) return 0
  if (serviceType === 'pickup') return Number(vehicle.pickup_price || 0)
  if (serviceType === 'dropoff') return Number(vehicle.dropoff_price || 0)
  return Number(vehicle.combo_price || 0)
}

function vehiclePriceLabel(vehicle, serviceType = form.service_type) {
  const price = vehicleServicePrice(vehicle, serviceType)
  if (price > 0) return `¥${price}`
  return t('transfer.priceToConfirm')
}

const basePrice = computed(() => vehicleServicePrice(selectedVehicle.value, form.service_type))

const servicePriceTip = computed(() => {
  if (!selectedVehicle.value) return ''
  const pickup = vehicleServicePrice(selectedVehicle.value, 'pickup')
  const dropoff = vehicleServicePrice(selectedVehicle.value, 'dropoff')
  const combo = vehicleServicePrice(selectedVehicle.value, 'combo')
  if (form.service_type === 'combo') {
    return ''
  }
  if (form.service_type === 'pickup' && pickup > 0) {
    return t('transfer.servicePriceTip', { price: pickup })
  }
  if (form.service_type === 'dropoff' && dropoff > 0) {
    return t('transfer.servicePriceTip', { price: dropoff })
  }
  return ''
})

const totalPrice = computed(() => basePrice.value)

function airportName(code) {
  if (code === 'PVG') return t('transfer.pudongAirport') + ' (PVG)'
  if (code === 'SHA') return t('transfer.hongqiaoAirport') + ' (SHA)'
  return code
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function vehicleCapacityText(vehicle) {
  if (!vehicle) return ''
  if (vehicle.capacity_desc) return vehicle.capacity_desc

  const parts = []
  if (vehicle.luggage_28) parts.push(t('transfer.luggageSize28', { n: vehicle.luggage_28 }))
  if (vehicle.luggage_24) parts.push(t('transfer.luggageSize24', { n: vehicle.luggage_24 }))
  if (parts.length) return parts.join(' + ')
  if (vehicle.luggage_capacity) return t('transfer.luggage', { n: vehicle.luggage_capacity })
  return ''
}

function vehiclePrimaryImage(vehicle) {
  if (!vehicle) return ''
  if (Array.isArray(vehicle.images) && vehicle.images.length) return vehicle.images[0]
  return vehicle.image || ''
}

function vehicleImageList(vehicle) {
  if (!vehicle) return []
  const images = Array.isArray(vehicle.images) && vehicle.images.length ? vehicle.images : (vehicle.image ? [vehicle.image] : [])
  return images.map(img => resolveUrl(img)).filter(Boolean)
}

function onDateConfirm({ selectedValues }) {
  const [y, m, d] = selectedValues
  const val = `${y}-${m}-${d}T00:00:00`
  if (activeDatePicker.value === 'dropoff') {
    dropoffFlightTime.value = val
  } else {
    form.flight_time = val
  }
  showDatePicker.value = false
}

function setPreviewIndex(index) {
  previewIndex.value = index
  previewImage.value = previewImages.value[index] || ''
}

function onPreviewTouchStart(e) {
  const touch = e.touches?.[0]
  if (!touch) return
  previewTouchStartX.value = touch.clientX
  previewTouchStartY.value = touch.clientY
}

function onPreviewTouchEnd(e) {
  const touch = e.changedTouches?.[0]
  if (!touch) return
  const deltaX = touch.clientX - previewTouchStartX.value
  const deltaY = touch.clientY - previewTouchStartY.value
  if (Math.abs(deltaX) < 40 || Math.abs(deltaX) < Math.abs(deltaY)) return
  if (deltaX > 0) showPrevPreview()
  else showNextPreview()
}

function showPrevPreview() {
  if (!previewImages.value.length) return
  const nextIndex = previewIndex.value <= 0 ? previewImages.value.length - 1 : previewIndex.value - 1
  setPreviewIndex(nextIndex)
}

function showNextPreview() {
  if (!previewImages.value.length) return
  const nextIndex = previewIndex.value >= previewImages.value.length - 1 ? 0 : previewIndex.value + 1
  setPreviewIndex(nextIndex)
}

function previewVehicle(vehicle) {
  const images = vehicleImageList(vehicle)
  if (!images.length) return
  previewImages.value = images
  previewTitle.value = vehicle.name || ''
  setPreviewIndex(0)
  showImagePreview.value = true
}

function validationFail(msg) {
  errorMsg.value = msg
  // Scroll to bottom where the error banner is (above submit button)
  setTimeout(() => {
    const banner = document.querySelector('.error-banner')
    if (banner) banner.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 50)
  // Auto-clear after 5 seconds
  setTimeout(() => { errorMsg.value = '' }, 5000)
}

async function onSubmit() {
  const st = form.service_type

  // Vehicle
  if (!form.vehicle_id) { validationFail(t('transfer.selectVehicle')); return }

  // Pickup validation
  if (st === 'pickup' || st === 'combo') {
    if (!form.pickup_airport) { validationFail(t('transfer.selectAirportTip')); return }
    if (!form.flight_no.trim()) { validationFail(t('transfer.flightNoRequired')); return }
  }

  // Dropoff validation
  if (st === 'dropoff') {
    if (!dropoffAirport.value) { validationFail(t('transfer.selectAirportTip')); return }
    if (!dropoffFlightNo.value.trim()) { validationFail(t('transfer.flightNoRequired')); return }
  }
  if (st === 'combo') {
    if (!dropoffAirport.value) { validationFail(t('transfer.selectAirportTip')); return }
    if (!dropoffFlightNo.value.trim()) { validationFail(t('transfer.flightNoRequired')); return }
  }

  // Booking number
  if (!form.booking_no.trim()) { validationFail(t('transfer.bookingNoRequired')); return }

  // Contact
  if (!form.contact_name.trim()) { validationFail(t('transfer.contactNameRequired')); return }
  if (!form.contact_phone.trim() && !form.contact_email.trim()) { validationFail(t('checkout.phoneOrEmail')); return }

  // Terms agreement
  if (!agreeTerms.value) { validationFail(t('transfer.agreeRequired')); return }

  // All validation passed, clear error
  errorMsg.value = ''

  // Build payload
  if (basePrice.value <= 0) { validationFail(t('transfer.priceNotConfigured')); return }

  const data = {
    service_type: st,
    vehicle_id: form.vehicle_id,
    booking_no: form.booking_no,
    contact_name: form.contact_name,
    contact_phone: form.contact_phone,
    contact_email: form.contact_email,
    remark: form.remark
  }

  // Flight info per service type
  if (st === 'pickup') {
    data.pickup_airport = form.pickup_airport
    data.flight_no = form.flight_no
    data.flight_time = form.flight_time
  } else if (st === 'dropoff') {
    data.dropoff_airport = dropoffAirport.value
    data.flight_no = dropoffFlightNo.value
    data.flight_time = dropoffFlightTime.value
  } else {
    // combo
    data.pickup_airport = form.pickup_airport
    data.flight_no = form.flight_no
    data.flight_time = form.flight_time
    data.dropoff_airport = dropoffAirport.value
    data.dropoff_flight_no = dropoffFlightNo.value
    data.dropoff_flight_time = dropoffFlightTime.value
  }

  submitting.value = true
  try {
    const res = await createTransferOrder(data)
    pendingOrderNo.value = res.data.order_no
    pendingAmount.value = res.data.total_price
    goToResult()
  } catch (e) {
    showToast(e.message)
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
      type: 'transfer'
    }
  })
}

onMounted(async () => {
  // 从 URL 参数读取服务类型
  const serviceType = route.query.service_type
  if (serviceType && ['pickup', 'dropoff', 'combo'].includes(serviceType)) {
    form.service_type = serviceType
  }

  try {
    const [vRes] = await Promise.all([
      getVehicles()
    ])
    vehicles.value = vRes.data || []

    const routeVehicleId = route.query.vehicle_id ? Number(route.query.vehicle_id) : null
    const matchedVehicle = routeVehicleId ? vehicles.value.find(v => v.id === routeVehicleId) : null
    if (matchedVehicle) {
      form.vehicle_id = matchedVehicle.id
    } else if (vehicles.value.length) {
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
.page-container {
  padding-top: 0;
}

.required {
  color: #ee0a24;
  font-weight: bold;
}

.field-hint {
  font-size: 11px;
  color: #999;
  margin-left: 4px;
}

.field-label {
  font-size: 14px;
  color: #333;
  padding: 8px 0 6px;
  font-weight: 500;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pickup-title {
  color: #1a73e8;
}

.dropoff-title {
  color: #e6a23c;
}

.airport-radios {
  display: flex;
  gap: 12px;
  padding: 4px 0 12px;
}

.airport-label {
  font-size: 14px;
}

.airport-code {
  display: inline-block;
  background: #f0f0f0;
  color: #666;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: 2px;
  font-family: monospace;
}

.route-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8f7f5;
  border-radius: 10px;
  padding: 12px;
  margin-top: 12px;
}

.route-point {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #333;
  flex: 1;
  min-width: 0;
}

.route-point span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-arrow {
  font-size: 18px;
  color: #bbb;
  flex-shrink: 0;
}

.service-radios {
  gap: 12px;
}

.entry-discount-banner {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  max-width: fit-content;
  margin: 0 0 12px;
  padding: 8px 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, #fffaf2 0%, #fff4e4 100%);
  border: 1px solid #f2dcc0;
  box-shadow: none;
}

.entry-discount-banner.active {
  border-color: #eccfaa;
  box-shadow: none;
}

.entry-discount-badge {
  flex-shrink: 0;
  min-width: 34px;
  height: 34px;
  padding: 0 7px;
  border-radius: 999px;
  background: #f6ead5;
  color: #b68443;
  font-size: 13px;
  font-weight: 800;
  line-height: 34px;
  text-align: center;
}

.entry-discount-text {
  font-size: 13px;
  font-weight: 700;
  color: #b68443;
  line-height: 1.4;
  white-space: nowrap;
}

.combo-tip {
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  background: linear-gradient(135deg, #fff8ec 0%, #fff3de 100%);
  border: 1px solid #f2dcc0;
}

.combo-tip-title {
  font-size: 13px;
  font-weight: 700;
  color: #8b5e1a;
  line-height: 1.4;
}

.combo-tip-desc {
  margin-top: 4px;
  font-size: 12px;
  color: #a06f2f;
  line-height: 1.5;
}

.service-tip {
  font-size: 12px;
  color: var(--accent);
}

.vehicle-intro {
  margin-bottom: 14px;
}

.vehicle-intro-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.vehicle-intro-desc {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vehicle-card {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  text-align: left;
}

.vehicle-card.active {
  border-color: var(--primary);
  background: var(--primary-light);
}

.vehicle-icon {
  width: 88px;
  height: 88px;
  border-radius: 12px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.vehicle-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: zoom-in;
}

.vehicle-card.active .vehicle-icon {
  background: rgba(26, 115, 232, 0.1);
}

.vehicle-image-badge {
  position: absolute;
  right: 4px;
  bottom: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 9px;
  background: rgba(0, 0, 0, 0.72);
  color: #fff;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
}

.vehicle-info {
  flex: 1;
  min-width: 0;
}

.vehicle-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.vehicle-name {
  font-size: 15px;
  font-weight: 700;
}

.vehicle-state-tag {
  padding: 2px 8px;
  border-radius: 999px;
  background: #f6f1e7;
  color: #8b6f47;
  font-size: 11px;
  font-weight: 600;
}

.vehicle-model {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.vehicle-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.vehicle-highlight-chip {
  padding: 4px 8px;
  border-radius: 999px;
  background: #f7f8fa;
  font-size: 11px;
  color: #4f5b6b;
}

.vehicle-desc {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 8px;
}

.vehicle-side {
  min-width: 84px;
  text-align: right;
  flex-shrink: 0;
}

.vehicle-price-label {
  font-size: 11px;
  color: var(--text-light);
}

.vehicle-price {
  margin-top: 4px;
  font-size: 18px;
  color: var(--accent);
  font-weight: 700;
}

.vehicle-side-tip {
  margin-top: 6px;
  font-size: 11px;
  color: var(--text-light);
  line-height: 1.4;
}

.booking-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
  line-height: 1.5;
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

.agree-card { padding: 12px 16px; }
.agree-text { font-size: 12px; color: var(--text-secondary); line-height: 1.6; }
.agree-link { color: var(--accent); text-decoration: underline; }

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 500;
  animation: shake 0.4s ease-in-out;
}

.image-preview-popup {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.88);
}

.image-preview-wrapper {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 16px 24px;
  box-sizing: border-box;
}

.image-preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
}

.image-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: #333;
  font-size: 36px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 5;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}

.image-nav:hover {
  background: #fff;
}

.image-nav-prev {
  left: 24px;
}

.image-nav-next {
  right: 24px;
}

.image-preview-title {
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 92px;
  text-align: center;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
}

.image-preview-count {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  opacity: 0.9;
}

.image-preview-thumbs {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 20px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px;
}

.image-preview-thumb {
  width: 56px;
  height: 56px;
  padding: 0;
  border: 2px solid transparent;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.15);
  flex: 0 0 auto;
}

.image-preview-thumb.active {
  border-color: #fff;
}

.image-preview-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

@media (max-width: 768px) {
  .image-nav {
    width: 46px;
    height: 46px;
    font-size: 30px;
  }

  .image-nav-prev {
    left: 12px;
  }

  .image-nav-next {
    right: 12px;
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-6px); }
  75% { transform: translateX(6px); }
}
</style>
