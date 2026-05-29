<template>
  <div class="page-container ticket-detail-page">
    <van-nav-bar :title="detail?.name || t('tickets.detailTitle')" left-arrow @click-left="$router.back()">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <div v-if="loading" class="loading-wrap">
      <van-loading size="24" />
    </div>

    <template v-else-if="detail">
      <section v-if="isDesktop" class="ticket-detail-desktop section-container">
        <div class="ticket-detail-desktop__hero">
          <div class="ticket-detail-desktop__gallery card">
            <div class="main-image-wrap" :class="{ empty: !currentImage }">
              <img v-if="currentImage" :src="resolveUrl(currentImage)" class="main-image" @click="previewDetailImages" />
              <div v-else class="image-placeholder">{{ detail.name?.charAt(0) || 'T' }}</div>
              <button
                v-if="imageList.length > 1"
                type="button"
                class="gallery-nav gallery-nav--prev"
                :aria-label="t('common.previous') || 'Prev'"
                @click.stop="prevImage"
              >‹</button>
              <button
                v-if="imageList.length > 1"
                type="button"
                class="gallery-nav gallery-nav--next"
                :aria-label="t('common.next') || 'Next'"
                @click.stop="nextImage"
              >›</button>
              <span v-if="imageList.length > 1" class="gallery-counter">{{ activeImage + 1 }} / {{ imageList.length }}</span>
            </div>

            <div v-if="imageList.length > 1" class="thumbnail-list thumbnail-list--desktop">
              <div
                v-for="(img, i) in imageList"
                :key="i"
                class="thumbnail-item"
                :class="{ active: activeImage === i }"
                @click="onThumbnailClick(i)"
              >
                <img :src="resolveUrl(img)" class="thumbnail-img" />
              </div>
            </div>
          </div>

          <div class="ticket-detail-desktop__summary card">
            <div class="ticket-detail-desktop__summary-top">
              <div>
                <div class="ticket-detail-desktop__heading-row">
                  <h1 class="detail-title detail-title--desktop">{{ detail.name }}</h1>
                  <span class="ticket-detail-desktop__city">{{ detail.city || t('tickets.cityShanghai') }}</span>
                </div>
                <p v-if="detail.subtitle" class="detail-subtitle detail-subtitle--desktop">{{ detail.subtitle }}</p>
                <div class="meta-row meta-row--desktop">
                  <span v-if="detail.category" class="meta-chip">{{ detail.category }}</span>
                  <span v-if="detail.real_name_required" class="meta-chip">{{ t('tickets.realNameRequired') }}</span>
                  <span v-if="detail.passport_required" class="meta-chip">{{ t('tickets.passportRequired') }}</span>
                  <span v-if="detail.featured" class="meta-chip meta-chip--featured">{{ t('tickets.featured') }}</span>
                </div>
              </div>
              <div class="ticket-detail-desktop__price-box">
                <div class="ticket-detail-desktop__price-label">{{ t('tickets.startingFrom') }}</div>
                <div class="ticket-detail-desktop__price">{{ minPrice ? `¥${minPrice}` : t('tickets.priceToConfirm') }}</div>
              </div>
            </div>

            <div class="ticket-detail-desktop__info-grid">
              <div v-if="detail.open_hours" class="ticket-detail-desktop__info-item">
                <div class="ticket-detail-desktop__info-label">{{ t('tickets.openHours') }}</div>
                <div class="ticket-detail-desktop__info-value">{{ detail.open_hours }}</div>
              </div>
              <div v-if="detail.address" class="ticket-detail-desktop__info-item">
                <div class="ticket-detail-desktop__info-label">{{ t('tickets.address') }}</div>
                <div class="ticket-detail-desktop__info-value">
                  {{ detail.address }}
                  <span v-if="desktopAmapLink || desktopGoogleMapLink" class="ticket-detail-desktop__map-links">
                    <a v-if="desktopAmapLink" :href="desktopAmapLink" target="_blank" rel="noreferrer" class="ticket-detail-desktop__map-link">{{ t('tickets.openAmap') }}</a>
                    <a v-if="desktopGoogleMapLink" :href="desktopGoogleMapLink" target="_blank" rel="noreferrer" class="ticket-detail-desktop__map-link ticket-detail-desktop__map-link--secondary">{{ t('tickets.openGoogleMaps') }}</a>
                  </span>
                </div>
              </div>
              <div class="ticket-detail-desktop__info-item">
                <div class="ticket-detail-desktop__info-label">{{ t('tickets.transportGuide') }}</div>
                <div class="ticket-detail-desktop__info-value">{{ t('tickets.desktopTrafficIntro') }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="ticket-detail-anchor-bar">
          <button type="button" class="ticket-detail-anchor-bar__item" :class="{ active: activeAnchor === 'booking' }" @click="scrollToSection('booking')">{{ t('tickets.ticketBooking') }}</button>
          <button type="button" class="ticket-detail-anchor-bar__item" :class="{ active: activeAnchor === 'intro' }" @click="scrollToSection('intro')">{{ t('tickets.description') }}</button>
          <button type="button" class="ticket-detail-anchor-bar__item" :class="{ active: activeAnchor === 'transport' }" @click="scrollToSection('transport')">{{ t('tickets.transportGuide') }}</button>
        </div>
      </section>

      <div v-else class="gallery-section">
        <div class="main-image-wrap" :class="{ empty: !currentImage }">
          <img v-if="currentImage" :src="resolveUrl(currentImage)" class="main-image" @click="previewDetailImages" />
          <div v-else class="image-placeholder">{{ detail.name?.charAt(0) || 'T' }}</div>
          <button
            v-if="imageList.length > 1"
            type="button"
            class="gallery-nav gallery-nav--prev"
            :aria-label="t('common.previous') || 'Prev'"
            @click.stop="prevImage"
          >‹</button>
          <button
            v-if="imageList.length > 1"
            type="button"
            class="gallery-nav gallery-nav--next"
            :aria-label="t('common.next') || 'Next'"
            @click.stop="nextImage"
          >›</button>
          <span v-if="imageList.length > 1" class="gallery-counter">{{ activeImage + 1 }} / {{ imageList.length }}</span>
        </div>

        <div v-if="imageList.length > 1" class="thumbnail-list">
          <div
            v-for="(img, i) in imageList"
            :key="i"
            class="thumbnail-item"
            :class="{ active: activeImage === i }"
            @click="onThumbnailClick(i)"
          >
            <img :src="resolveUrl(img)" class="thumbnail-img" />
          </div>
        </div>
      </div>

      <div v-if="!isDesktop" class="card intro-card">
        <div class="title-row">
          <h1 class="detail-title">{{ detail.name }}</h1>
          <van-tag v-if="detail.featured" type="warning" round>{{ t('tickets.featured') }}</van-tag>
        </div>
        <p v-if="detail.subtitle" class="detail-subtitle">{{ detail.subtitle }}</p>
        <div class="meta-row">
          <span v-if="detail.city" class="meta-chip">{{ detail.city }}</span>
          <span v-if="detail.category" class="meta-chip">{{ detail.category }}</span>
          <span v-if="detail.real_name_required" class="meta-chip">{{ t('tickets.realNameRequired') }}</span>
          <span v-if="detail.passport_required" class="meta-chip">{{ t('tickets.passportRequired') }}</span>
        </div>
        <div class="price-box">
          <div class="price-label">{{ t('tickets.startingFrom') }}</div>
          <div class="price-value">{{ minPrice ? `¥${minPrice}` : t('tickets.priceToConfirm') }}</div>
        </div>
      </div>

      <div class="detail-body">
        <div class="detail-main">
          <div id="ticket-booking-section" ref="bookingSectionRef" class="card package-card desktop-package-card">
            <div class="package-header-row">
              <div class="card-title package-card-title">{{ t('tickets.availablePackages') }}</div>
              <button type="button" class="ticket-cart-link" @click="goTicketCart">
                {{ t('common.cart') }}<span v-if="ticketCartCount" class="ticket-cart-badge">{{ ticketCartCount }}</span>
              </button>
            </div>
            <div class="package-list package-list--horizontal">
              <div
                v-for="pkg in packages"
                :key="pkg.id"
                class="package-item package-item--horizontal"
                :class="{ active: activePackageId === pkg.id }"
                @click="setActivePackage(pkg.id)"
              >
                <div class="package-main package-main--horizontal">
                  <div class="package-copy">
                    <div class="package-name">{{ pkg.package_name }}</div>
                    <div class="package-type">{{ ticketTypeLabel(pkg.ticket_type) }}</div>
                  </div>
                  <div class="package-price-wrap">
                    <div class="package-price">¥{{ displayPackagePrice(pkg) }}</div>
                    <div v-if="pkg.original_price" class="package-original">¥{{ pkg.original_price }}</div>
                  </div>
                </div>
                <div class="package-quantity-row">
                  <span class="package-quantity-label">{{ t('tickets.quantity') }}</span>
                  <div class="qty-stepper" @click.stop>
                    <button type="button" class="qty-btn" :disabled="getPackageQuantity(pkg.id) <= 0" @click.stop="decreasePackageQuantity(pkg.id)">−</button>
                    <span class="qty-value">{{ getPackageQuantity(pkg.id) }}</span>
                    <button type="button" class="qty-btn" @click.stop="increasePackageQuantity(pkg.id)">+</button>
                  </div>
                </div>
                <div class="package-detail-toggle-row">
                  <button type="button" class="package-detail-toggle" @click.stop="togglePackageDetail(pkg.id)">
                    {{ expandedPackageIds.includes(pkg.id) ? '收起详情' : t('tickets.viewDetail') }}
                  </button>
                </div>
                <div v-if="expandedPackageIds.includes(pkg.id)" class="package-detail-panel">
                  <div v-if="pkg.age_rule" class="package-note">{{ pkg.age_rule }}</div>
                  <div v-if="pkg.booking_notice" class="package-note">{{ pkg.booking_notice }}</div>
                </div>
              </div>
            </div>
          </div>

          <div id="ticket-intro-section" ref="introSectionRef" class="card info-card info-card--desktop">
            <div class="card-title card-title--desktop">{{ t('tickets.description') }}</div>
            <div v-if="detail.desc" class="info-value multiline info-value--desktop">{{ detail.desc }}</div>
            <div v-else class="info-value info-value--desktop">{{ detail.subtitle || t('tickets.desktopListFallback') }}</div>
          </div>

          <div v-if="detail.visit_notice" class="card rules-card">
            <div class="card-title card-title--desktop">{{ t('tickets.visitNotice') }}</div>
            <div class="rule-text">{{ detail.visit_notice }}</div>
          </div>

          <div v-if="detail.refund_rule" class="card rules-card">
            <div class="card-title card-title--desktop">{{ t('tickets.refundRule') }}</div>
            <div class="rule-text">{{ detail.refund_rule }}</div>
          </div>

          <div id="ticket-transport-section" ref="transportSectionRef" class="card traffic-guide-card">
            <div class="card-title card-title--desktop">{{ t('tickets.transportGuide') }}</div>
            <div class="traffic-guide-card__map traffic-guide-card__map--full">
              <div class="traffic-guide-card__map-title">{{ t('tickets.address') }}</div>
              <div class="traffic-guide-card__map-address">{{ detail.address || t('common.noData') }}</div>
              <div class="traffic-guide-card__map-hours">
                <strong>{{ t('tickets.openHours') }}：</strong>{{ detail.open_hours || t('common.noData') }}
              </div>
              <div v-if="desktopAmapLink || desktopGoogleMapLink" class="traffic-guide-card__map-actions">
                <a v-if="desktopAmapLink" :href="desktopAmapLink" target="_blank" rel="noreferrer" class="traffic-guide-card__map-link">{{ t('tickets.openAmap') }}</a>
                <a v-if="desktopGoogleMapLink" :href="desktopGoogleMapLink" target="_blank" rel="noreferrer" class="traffic-guide-card__map-link traffic-guide-card__map-link--secondary">{{ t('tickets.openGoogleMaps') }}</a>
              </div>
            </div>
          </div>

          <div class="card transport-panel-card">
            <div class="transport-panel-card__head">
              <div>
                <div class="card-title card-title--desktop transport-panel-card__title">{{ t('tickets.optionalTransfer') }}</div>
                <div class="transport-panel-card__subtitle">{{ t('tickets.transferBookingTip') }}</div>
              </div>
              <div v-if="transportVehicleCards.length" class="transport-panel-card__badge">{{ t('tickets.roundTrip') }}</div>
            </div>

            <div class="transport-list transport-list--inline">
              <div class="transport-item" :class="{ active: selectedTransportId === '' }" @click="selectedTransportId = ''">
                <div>
                  <div class="transport-name">{{ t('tickets.noTransfer') }}</div>
                  <div class="transport-desc">{{ t('tickets.transferOptionalTip') }}</div>
                </div>
              </div>
            </div>

            <div v-if="transportVehicleCards.length" class="transport-hero-panel transport-hero-panel--embedded">
              <div class="transport-hero-panel__eyebrow">{{ t('tickets.transferType') }}</div>
              <div class="transport-hero-panel__title">{{ t('tickets.roundTrip') }}</div>
              <div class="transport-hero-panel__desc">{{ t('tickets.transferTypeHint') }}</div>
            </div>
            <div v-if="transportVehicleCards.length" class="vehicle-list ticket-transfer-vehicle-list ticket-transfer-vehicle-list--main">
              <div
                v-for="card in transportVehicleCards"
                :key="card.key"
                class="vehicle-card vehicle-card--transport"
                :class="{ active: isVehicleTransportSelected(card) }"
                role="button"
                tabindex="0"
                @click="selectVehicleTransport(card)"
                @keydown.enter.prevent="selectVehicleTransport(card)"
                @keydown.space.prevent="selectVehicleTransport(card)"
              >
                <div class="vehicle-card__top">
                  <div class="vehicle-icon vehicle-icon--large">
                    <img
                      v-if="vehiclePrimaryImage(card.vehicle)"
                      :src="resolveUrl(vehiclePrimaryImage(card.vehicle))"
                      :alt="vehicleDisplayName(card.vehicle)"
                      class="vehicle-img"
                      @click.stop="previewVehicle(card.vehicle)"
                    />
                    <div v-if="(card.vehicle?.images?.length || 0) > 1" class="vehicle-image-badge">{{ card.vehicle.images.length }}</div>
                  </div>
                  <div class="vehicle-info">
                    <div class="vehicle-name-row">
                      <div class="vehicle-name">{{ vehicleDisplayName(card.vehicle) }}</div>
                      <span class="vehicle-state-tag">{{ isVehicleTransportSelected(card) ? t('transfer.selectedVehicle') : transferServiceLabel(getVehicleTransportOption(card)?.service_type) }}</span>
                    </div>
                    <div v-if="card.vehicle?.model" class="vehicle-model">车型：{{ card.vehicle.model }}</div>
                    <div class="vehicle-highlights">
                      <span class="vehicle-highlight-chip">{{ t('transfer.seats', { n: card.vehicle?.seats || 0 }) }}</span>
                      <span v-if="vehicleCapacityText(card.vehicle)" class="vehicle-highlight-chip">{{ vehicleCapacityText(card.vehicle) }}</span>
                    </div>
                    <div v-if="vehicleImageList(card.vehicle).length > 1" class="vehicle-thumb-row" @click.stop>
                      <span
                        v-for="(img, index) in vehicleImageList(card.vehicle).slice(0, 4)"
                        :key="`${card.key}-${img}-${index}`"
                        class="vehicle-thumb"
                        @click="previewVehicle(card.vehicle, index)"
                      >
                        <img :src="img" :alt="`${vehicleDisplayName(card.vehicle)}-${index + 1}`" />
                      </span>
                    </div>
                    <div class="vehicle-desc">{{ t('transfer.vehicleGalleryHint') }}</div>
                  </div>
                  <div class="vehicle-side vehicle-side--boxed">
                    <div class="vehicle-side-select-label">{{ t('tickets.transferType') }}</div>
                    <select class="vehicle-service-select" :value="getVehicleSelectedServiceType(card)" @click.stop @change.stop="onVehicleServiceTypeChange(card, $event.target.value)">
                      <option v-for="serviceType in card.serviceTypes" :key="`${card.key}-${serviceType}`" :value="serviceType">{{ transferServiceLabel(serviceType) }}</option>
                    </select>
                    <div class="vehicle-price-label">{{ t('transfer.approxPrice') }}</div>
                    <div class="vehicle-price">¥{{ getVehicleTransportOption(card)?.price ?? 0 }}</div>
                    <div class="vehicle-side-tip">{{ t('transfer.tapToPreview') }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="transport-empty-state">
              <div class="transport-empty-state__title">{{ t('tickets.transferUnavailableTitle') }}</div>
              <div class="transport-empty-state__desc">{{ t('tickets.transferUnavailableDesc') }}</div>
            </div>
          </div>
        </div>

        <aside class="detail-sidebar">
          <div class="card calendar-card booking-card">
            <div class="card-title">{{ t('tickets.visitDate') }}</div>
            <div class="calendar-head">
              <div>
                <div class="calendar-selected-label">{{ t('tickets.selectedDateLabel') }}</div>
                <div class="calendar-selected-value">{{ selectedVisitDateText }}</div>
              </div>
              <div class="calendar-month-switch">
                <button type="button" class="month-btn" :disabled="!canGoPrevMonth" @click="changeMonth(-1)">‹</button>
                <span class="month-title">{{ currentMonthLabel }}</span>
                <button type="button" class="month-btn" :disabled="!canGoNextMonth" @click="changeMonth(1)">›</button>
              </div>
            </div>
            <div class="booking-window-tip">{{ bookingWindowText }}</div>
            <div class="weekday-row">
              <span v-for="item in weekDays" :key="item">{{ item }}</span>
            </div>
            <div class="calendar-grid">
              <button
                v-for="day in calendarCells"
                :key="day.key"
                type="button"
                class="calendar-day"
                :class="{
                  empty: !day.date,
                  disabled: day.date && !day.selectable,
                  selected: day.date && selectedVisitDate === day.iso,
                  today: day.date && day.isToday
                }"
                :disabled="!day.date || !day.selectable"
                @click="selectVisitDate(day)"
              >
                <template v-if="day.date">
                  <span v-if="day.rule?.tag" class="day-tag">{{ day.rule.tag }}</span>
                  <span class="day-number">{{ day.dayNumber }}</span>
                  <span class="day-price">{{ day.priceText }}</span>
                </template>
              </button>
            </div>
          </div>


          <div class="card booking-summary-card booking-card">
            <div class="booking-summary__meta">{{ t('tickets.selectedPackage') }}</div>
            <div v-if="selectedPackages.length" class="booking-selected-list">
              <div v-for="pkg in selectedPackages" :key="pkg.id" class="booking-selected-item">
                <div>
                  <div class="booking-selected-name">{{ pkg.package_name }}</div>
                  <div class="booking-selected-count">x{{ pkg.quantity }}</div>
                </div>
                <div class="booking-selected-subtotal">¥{{ getPackageSubtotal(pkg) }}</div>
              </div>
            </div>
            <div v-else class="booking-summary__title">{{ t('tickets.selectPackageFirst') }}</div>
            <div class="booking-summary__date">{{ selectedVisitDateText }}</div>
            <div class="booking-summary__qty">{{ t('tickets.quantity') }}：{{ totalSelectedQuantity }}</div>
            <div v-if="selectedTransportOption" class="booking-summary__transfer">
              {{ transferServiceLabel(selectedTransportOption.service_type) }} · {{ selectedTransportOption.vehicle?.name || selectedTransportOption.vehicle?.name_zh || '-' }} +¥{{ selectedTransportOption.price }}
            </div>
            <div class="booking-summary__price">¥{{ totalWithTransportPrice }}</div>
            <div class="booking-summary__actions">
              <van-button plain block round size="large" :disabled="!selectedVisitDate || !selectedPackages.length" @click="addTicketCart">
                {{ t('shop.addToCart') }}
              </van-button>
              <van-button type="primary" block round size="large" :disabled="!selectedVisitDate || !selectedPackages.length" @click="goCheckout">
                {{ t('tickets.bookNow') }}
              </van-button>
            </div>
          </div>
        </aside>
      </div>

      <!-- 用户评价区 -->
      <div class="card ticket-reviews-card" v-if="detail">
        <div class="ticket-reviews-card__head">
          <h3 class="ticket-reviews-card__title">⭐ {{ t('review.sectionTitle') }}</h3>
          <div v-if="reviewStats.total > 0" class="ticket-reviews-card__stat">
            <span class="ticket-reviews-card__avg">{{ reviewStats.avg_rating }}</span>
            <van-rate :model-value="reviewStats.avg_rating || 0" readonly allow-half size="14" color="#ffd21e" void-color="#e0e0e0" />
            <span class="ticket-reviews-card__count">({{ t('review.reviewCount', { count: reviewStats.total }) }})</span>
          </div>
        </div>

        <div v-if="reviewLoading" class="ticket-reviews-card__loading">
          <van-loading size="20" />
        </div>

        <template v-else-if="reviewList.length">
          <div v-for="r in reviewList" :key="r.id" class="ticket-review-item">
            <div class="ticket-review-item__head">
              <van-rate :model-value="r.rating" readonly size="13" color="#ffd21e" void-color="#e0e0e0" />
              <span class="ticket-review-item__name">{{ r.reviewer_name || '匿名' }}</span>
              <span class="ticket-review-item__date">{{ formatReviewDate(r.created_at) }}</span>
            </div>
            <div v-if="r.comment" class="ticket-review-item__comment">{{ r.comment }}</div>
            <div v-if="r.admin_reply" class="ticket-review-item__reply">
              <span class="ticket-review-item__reply-label">{{ t('review.adminReplyLabel') }}：</span>{{ r.admin_reply }}
            </div>
          </div>
        </template>

        <div v-else class="ticket-reviews-card__empty">{{ t('review.noReviews') }}</div>
      </div>

      <div class="bottom-action mobile-bottom-action">
        <div>
          <div class="bottom-action__label">{{ t('tickets.selectedPackage') }}</div>
          <div class="bottom-action__value">{{ selectedPackages.length ? `${selectedPackages.length} ${t('tickets.availablePackages')}` : t('tickets.selectPackageFirst') }}</div>
          <div class="bottom-action__date">{{ selectedVisitDateText }} · {{ t('tickets.quantity') }} {{ totalSelectedQuantity }}</div>
          <div v-if="selectedTransportOption" class="bottom-action__date">{{ transferServiceLabel(selectedTransportOption.service_type) }} +¥{{ selectedTransportOption.price }}</div>
        </div>
        <van-button type="primary" round :disabled="!selectedPackages.length || !selectedVisitDate" @click="goCheckout">
          {{ t('tickets.bookNow') }} ¥{{ totalWithTransportPrice }}
        </van-button>
      </div>
    </template>

    <transition name="ticket-inline-notice-fade">
      <div
        v-if="ticketNoticeVisible"
        class="ticket-inline-notice"
        :class="`ticket-inline-notice--${ticketNoticeType}`"
      >
        {{ ticketNoticeText }}
      </div>
    </transition>

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
          <div class="image-preview-title__text">{{ previewTitle }}</div>
          <div v-if="previewVehicleInfo" class="image-preview-meta">
            <span v-if="previewVehicleInfo.seats" class="image-preview-meta__chip">{{ t('transfer.seats', { n: previewVehicleInfo.seats }) }}</span>
            <span v-if="vehicleCapacityText(previewVehicleInfo)" class="image-preview-meta__chip">{{ vehicleCapacityText(previewVehicleInfo) }}</span>
          </div>
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
import { ref, computed, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ImagePreview } from 'vant'
import { getTicketAttraction, getTicketTransportOptions } from '../api/tickets'
import { resolveUrl, getTicketReviews } from '../api'
import LangSwitch from '../components/LangSwitch.vue'
import { useCartStore } from '../stores/cart'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const cart = useCartStore()

const loading = ref(true)
const detail = ref(null)
const packages = ref([])
const transportOptions = ref([])
const activeImage = ref(0)
const showImagePreview = ref(false)
const previewImage = ref('')
const previewTitle = ref('')
const previewImages = ref([])
const previewIndex = ref(0)
const previewVehicleInfo = ref(null)
const previewTouchStartX = ref(0)
const previewTouchStartY = ref(0)
const activePackageId = ref(null)
const expandedPackageIds = ref([])
const packageQuantities = reactive({})
const vehicleServiceSelections = reactive({})
const selectedTransportId = ref('')
const selectedVisitDate = ref('')
const isDesktop = ref(window.innerWidth >= 1024)
const activeAnchor = ref('booking')
const bookingSectionRef = ref(null)
const introSectionRef = ref(null)
const transportSectionRef = ref(null)
const ticketNoticeVisible = ref(false)
const ticketNoticeText = ref('')
const ticketNoticeType = ref('info')
let ticketNoticeTimer = null
const today = new Date()
today.setHours(0, 0, 0, 0)
const bookingEndDate = new Date(today)
bookingEndDate.setMonth(bookingEndDate.getMonth() + 1)
const currentMonth = ref(getMonthStart(new Date()))

const weekDaysMap = {
  zh: ['日', '一', '二', '三', '四', '五', '六'],
  en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  ru: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  es: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa']
}

const weekDays = computed(() => weekDaysMap[locale.value] || weekDaysMap.zh)

const imageList = computed(() => {
  const imgs = detail.value?.images?.length ? detail.value.images : []
  if (detail.value?.cover_image && !imgs.includes(detail.value.cover_image)) {
    return [detail.value.cover_image, ...imgs]
  }
  return imgs.length ? imgs : (detail.value?.cover_image ? [detail.value.cover_image] : [])
})

const currentImage = computed(() => imageList.value[activeImage.value] || '')
const selectedPackage = computed(() => packages.value.find(item => item.id === activePackageId.value) || packages.value[0] || null)
const selectedPackages = computed(() => packages.value
  .filter(item => getPackageQuantity(item.id) > 0)
  .map(item => ({ ...item, quantity: getPackageQuantity(item.id) })))
const totalSelectedQuantity = computed(() => selectedPackages.value.reduce((sum, item) => sum + item.quantity, 0))
const totalSelectedPrice = computed(() => selectedPackages.value.reduce((sum, item) => sum + Number(getPackageSubtotal(item)), 0).toFixed(2))
const transportServiceOrder = ['round_trip', 'pickup_only', 'dropoff_only', 'charter']
const transportVehicleCards = computed(() => {
  const groups = new Map()

  for (const item of transportOptions.value || []) {
    const key = getTransportVehicleKey(item)
    if (!key) continue

    if (!groups.has(key)) {
      groups.set(key, {
        key,
        vehicle: item.vehicle || null,
        optionMap: {}
      })
    }

    const current = groups.get(key)
    if (!current.vehicle && item.vehicle) current.vehicle = item.vehicle
    current.optionMap[item.service_type] = item
  }

  return Array.from(groups.values())
    .map(group => {
      const serviceTypes = transportServiceOrder.filter(type => group.optionMap[type])
      Object.keys(group.optionMap).forEach(type => {
        if (!serviceTypes.includes(type)) serviceTypes.push(type)
      })

      return {
        ...group,
        serviceTypes,
        defaultServiceType: serviceTypes.includes('round_trip') ? 'round_trip' : (serviceTypes[0] || '')
      }
    })
    .sort((a, b) => {
      const sortDiff = Number(a.vehicle?.sort_order || 0) - Number(b.vehicle?.sort_order || 0)
      if (sortDiff !== 0) return sortDiff
      return Number(a.vehicle?.id || 0) - Number(b.vehicle?.id || 0)
    })
})
const selectedTransportOption = computed(() => transportOptions.value.find(item => String(item.id) === String(selectedTransportId.value)) || null)
const totalWithTransportPrice = computed(() => (Number(totalSelectedPrice.value) + Number(selectedTransportOption.value?.price || 0)).toFixed(2))
const minPrice = computed(() => {
  const values = packages.value.map(pkg => getPackageMinPrice(pkg)).filter(Boolean)
  return values.length ? Math.min(...values) : null
})

const currentMonthLabel = computed(() => {
  const y = currentMonth.value.getFullYear()
  const m = currentMonth.value.getMonth() + 1
  return locale.value === 'en' ? `${y}-${String(m).padStart(2, '0')}` : `${y}年${m}月`
})

const minBookingMonth = computed(() => getMonthStart(today))
const maxBookingMonth = computed(() => getMonthStart(bookingEndDate))
const canGoPrevMonth = computed(() => currentMonth.value.getTime() > minBookingMonth.value.getTime())
const canGoNextMonth = computed(() => currentMonth.value.getTime() < maxBookingMonth.value.getTime())
const bookingWindowText = computed(() => {
  if (locale.value === 'en') return `Bookable: ${formatDate(today)} ~ ${formatDate(bookingEndDate)}`
  return `可预订日期：${formatDate(today)} - ${formatDate(bookingEndDate)}`
})
const selectedVisitDateText = computed(() => formatDisplayDate(selectedVisitDate.value))
const ticketCartCount = computed(() => cart.ticketItemCount)
const desktopAmapLink = computed(() => {
  if (!detail.value?.address) return ''
  return `https://uri.amap.com/search?keyword=${encodeURIComponent(detail.value.address)}`
})
const desktopGoogleMapLink = computed(() => {
  if (!detail.value?.address) return ''
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(detail.value.address)}`
})

function getMonthStart(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function formatDisplayDate(isoDate) {
  if (!isoDate) return t('tickets.visitDatePlaceholder')
  const date = new Date(`${isoDate}T00:00:00`)
  const day = date.getDay()

  if (locale.value === 'zh') return `${isoDate} 星期${weekDaysMap.zh[day]}`
  return `${isoDate} ${weekDays.value[day]}`
}

function isDateWithinBookingWindow(date) {
  return date >= today && date <= bookingEndDate
}

function clampMonth(date) {
  const monthStart = getMonthStart(date)
  if (monthStart < minBookingMonth.value) return new Date(minBookingMonth.value)
  if (monthStart > maxBookingMonth.value) return new Date(maxBookingMonth.value)
  return monthStart
}

function getRuleMap(pkg) {
  const map = new Map()
  if (Array.isArray(pkg?.date_rules)) {
    pkg.date_rules.forEach(rule => {
      if (rule?.date) map.set(rule.date, rule)
    })
  }
  return map
}

function getPackageMinPrice(pkg) {
  if (!pkg) return null
  const basePrice = Number(pkg.sale_price || 0)
  if (Array.isArray(pkg.date_rules) && pkg.date_rules.length) {
    const prices = pkg.date_rules
      .filter(rule => rule?.enabled !== false && rule?.price !== undefined && rule?.price !== null)
      .map(rule => Number(rule.price))
      .filter(v => !Number.isNaN(v))
    if (!Number.isNaN(basePrice)) prices.unshift(basePrice)
    if (prices.length) return Math.min(...prices)
  }
  return Number.isNaN(basePrice) ? null : basePrice
}

function getPriceForDate(pkg, isoDate) {
  if (!pkg) return null
  const rule = getRuleMap(pkg).get(isoDate)
  if (rule) {
    if (rule.enabled === false) return null
    return Number(rule.price ?? pkg.sale_price)
  }
  return Number(pkg.sale_price || 0)
}

function isSelectableDate(pkg, isoDate) {
  if (!pkg) return false
  const current = new Date(`${isoDate}T00:00:00`)
  if (!isDateWithinBookingWindow(current)) return false

  const rule = getRuleMap(pkg).get(isoDate)
  if (rule) {
    return rule.enabled !== false
  }
  return true
}

function getEffectivePackages() {
  return selectedPackages.value.length ? selectedPackages.value : (selectedPackage.value ? [{ ...selectedPackage.value, quantity: 1 }] : [])
}

function isSelectableForCurrentSelection(isoDate) {
  const currentPackages = getEffectivePackages()
  if (!currentPackages.length) return false
  return currentPackages.every(pkg => isSelectableDate(pkg, isoDate))
}

function getCalendarPriceForDate(isoDate) {
  const currentPackages = getEffectivePackages()
  if (!currentPackages.length) return null
  return currentPackages.reduce((sum, pkg) => {
    const price = getPriceForDate(pkg, isoDate)
    if (price === null) return sum
    return sum + (Number(price) * Number(pkg.quantity || 1))
  }, 0)
}

function getFirstSelectableDate(pkgList = null) {
  const currentPackages = Array.isArray(pkgList)
    ? pkgList
    : (pkgList ? [pkgList] : getEffectivePackages())
  if (!currentPackages.length) return ''
  const cursor = new Date(today)
  while (cursor <= bookingEndDate) {
    const iso = formatDate(cursor)
    if (currentPackages.every(pkg => isSelectableDate(pkg, iso))) return iso
    cursor.setDate(cursor.getDate() + 1)
  }
  return ''
}

function getPackageQuantity(packageId) {
  return Number(packageQuantities[packageId] || 0)
}

function getPackageSubtotal(pkg) {
  const price = selectedVisitDate.value ? getPriceForDate(pkg, selectedVisitDate.value) : getPackageMinPrice(pkg)
  return ((Number(price || 0) * Number(pkg.quantity || getPackageQuantity(pkg.id) || 0))).toFixed(2)
}

function ensureSelectedDateIsValid() {
  if (selectedVisitDate.value && !isSelectableForCurrentSelection(selectedVisitDate.value)) {
    selectedVisitDate.value = ''
  }
  if (!selectedVisitDate.value) {
    selectedVisitDate.value = getFirstSelectableDate()
  }
  if (selectedVisitDate.value) {
    currentMonth.value = clampMonth(new Date(`${selectedVisitDate.value}T00:00:00`))
  }
}

function setActivePackage(id) {
  activePackageId.value = id
  ensureSelectedDateIsValid()
}

function togglePackageDetail(packageId) {
  if (expandedPackageIds.value.includes(packageId)) {
    expandedPackageIds.value = expandedPackageIds.value.filter(id => id !== packageId)
  } else {
    expandedPackageIds.value = [...expandedPackageIds.value, packageId]
  }
}

function setPackageQuantity(packageId, quantity) {
  const next = Math.max(0, Number(quantity || 0))
  packageQuantities[packageId] = next
  if (!activePackageId.value) {
    activePackageId.value = packageId
  }
  ensureSelectedDateIsValid()
}

function increasePackageQuantity(packageId) {
  setPackageQuantity(packageId, getPackageQuantity(packageId) + 1)
  activePackageId.value = packageId
}

function decreasePackageQuantity(packageId) {
  setPackageQuantity(packageId, getPackageQuantity(packageId) - 1)
}

const calendarCells = computed(() => {
  const result = []
  const start = new Date(currentMonth.value)
  const year = start.getFullYear()
  const month = start.getMonth()
  const firstWeekDay = start.getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  for (let i = 0; i < firstWeekDay; i += 1) {
    result.push({ key: `empty-${i}`, date: null })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month, day)
    const iso = formatDate(date)
    const pkg = selectedPackage.value
    const rule = getRuleMap(pkg).get(iso)
    const selectable = isSelectableForCurrentSelection(iso)
    const price = getCalendarPriceForDate(iso)
    const todayIso = formatDate(new Date())

    result.push({
      key: iso,
      date,
      iso,
      dayNumber: day,
      selectable,
      rule,
      isToday: iso === todayIso,
      priceText: selectable && price !== null ? `¥${price}` : ''
    })
  }

  while (result.length % 7 !== 0) {
    result.push({ key: `empty-tail-${result.length}`, date: null })
  }

  return result
})

function changeMonth(step) {
  currentMonth.value = clampMonth(new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + step, 1))
}

function selectPackage(id) {
  setActivePackage(id)
}

function selectVisitDate(day) {
  if (!day?.iso || !day.selectable) return
  selectedVisitDate.value = day.iso
  currentMonth.value = clampMonth(day.date)
}

function displayPackagePrice(pkg) {
  if (!pkg) return '-'
  if (selectedVisitDate.value) {
    const price = getPriceForDate(pkg, selectedVisitDate.value)
    if (price !== null) return price
  }
  return getPackageMinPrice(pkg) || pkg.sale_price || 0
}

function ticketTypeLabel(type) {
  const map = {
    adult: t('tickets.adultTicket'),
    child: t('tickets.childTicket'),
    senior: t('tickets.seniorTicket'),
    family: t('tickets.familyTicket'),
    combo: t('tickets.comboTicket')
  }
  return map[type] || type || '-'
}

function transferServiceLabel(type) {
  const map = {
    pickup_only: t('tickets.pickupOnly'),
    dropoff_only: t('tickets.dropoffOnly'),
    round_trip: t('tickets.roundTrip'),
    charter: t('tickets.charter')
  }
  return map[type] || type || '-'
}

function getTransportVehicleKey(item) {
  return String(item?.vehicle?.id || item?.vehicle_id || '')
}

function getVehicleSelectedServiceType(card) {
  if (!card) return ''
  return vehicleServiceSelections[card.key] || card.defaultServiceType || ''
}

function getVehicleTransportOption(card) {
  if (!card) return null
  const selectedType = getVehicleSelectedServiceType(card)
  return card.optionMap[selectedType] || card.optionMap[card.defaultServiceType] || null
}

function isVehicleTransportSelected(card) {
  const option = getVehicleTransportOption(card)
  return !!option && String(selectedTransportId.value) === String(option.id)
}

function selectVehicleTransport(card) {
  const option = getVehicleTransportOption(card)
  selectedTransportId.value = option ? String(option.id) : ''
}

function onVehicleServiceTypeChange(card, value) {
  if (!card) return
  vehicleServiceSelections[card.key] = value
  const option = card.optionMap[value] || null
  if (option) {
    selectedTransportId.value = String(option.id)
  }
}

function vehicleDisplayName(vehicle) {
  if (!vehicle) return ''
  return vehicle.name || vehicle.model || vehicle.name_zh || ''
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

function previewVehicle(vehicle, startIndex = 0) {
  const images = vehicleImageList(vehicle)
  if (!images.length) return
  previewImages.value = images
  previewVehicleInfo.value = vehicle || null
  previewTitle.value = vehicleDisplayName(vehicle)
  setPreviewIndex(startIndex)
  showImagePreview.value = true
}

watch(
  [transportVehicleCards, selectedTransportId],
  ([cards, currentSelectedId]) => {
    const validKeys = new Set(cards.map(card => card.key))

    Object.keys(vehicleServiceSelections).forEach(key => {
      if (!validKeys.has(key)) delete vehicleServiceSelections[key]
    })

    cards.forEach(card => {
      const matchedOption = card.serviceTypes
        .map(type => card.optionMap[type])
        .find(option => String(option?.id) === String(currentSelectedId))
      const nextType = matchedOption?.service_type || vehicleServiceSelections[card.key] || card.defaultServiceType

      vehicleServiceSelections[card.key] = card.serviceTypes.includes(nextType)
        ? nextType
        : card.defaultServiceType
    })
  },
  { immediate: true }
)

function previewDetailImages() {
  if (!imageList.value.length) return
  ImagePreview({
    images: imageList.value.map(item => resolveUrl(item)),
    startPosition: activeImage.value,
    closeable: true,
    showIndex: true,
    maxZoom: 5,   // 显式声明双指捏合最大放大倍数
    minZoom: 1 / 3
  })
}

function prevImage() {
  const total = imageList.value.length
  if (total < 2) return
  activeImage.value = (activeImage.value - 1 + total) % total
}

function nextImage() {
  const total = imageList.value.length
  if (total < 2) return
  activeImage.value = (activeImage.value + 1) % total
}

function onThumbnailClick(index) {
  // 第一次点缩略图先切到那张；再次点击当前缩略图则打开放大预览
  if (activeImage.value === index) {
    previewDetailImages()
  } else {
    activeImage.value = index
  }
}

function showInlineNotice(message, type = 'info') {
  if (!message) return
  ticketNoticeText.value = message
  ticketNoticeType.value = type
  ticketNoticeVisible.value = true
  if (ticketNoticeTimer) clearTimeout(ticketNoticeTimer)
  ticketNoticeTimer = window.setTimeout(() => {
    ticketNoticeVisible.value = false
    ticketNoticeTimer = null
  }, 1800)
}

function addTicketCart() {
  if (!selectedPackages.value.length) {
    showInlineNotice(t('tickets.selectPackageFirst'), 'error')
    return
  }
  if (!selectedVisitDate.value) {
    showInlineNotice(t('tickets.visitDateRequired'), 'error')
    return
  }

  cart.addTicketItem({
    attraction_id: detail.value.id,
    attraction_name: detail.value.name,
    attraction_image: imageList.value[0] || '',
    visit_date: selectedVisitDate.value,
    transport_price_id: selectedTransportId.value || '',
    packages: selectedPackages.value.map(item => ({
      package_id: item.id,
      package_name: item.package_name,
      quantity: item.quantity,
      ticket_type: item.ticket_type,
      price: displayPackagePrice(item)
    }))
  })

  showInlineNotice(t('tickets.added'), 'success')
}

function goTicketCart() {
  router.push('/cart?tab=ticket')
}

function goCheckout() {
  if (!selectedPackages.value.length) {
    showInlineNotice(t('tickets.selectPackageFirst'), 'error')
    return
  }
  if (!selectedVisitDate.value) {
    showInlineNotice(t('tickets.visitDateRequired'), 'error')
    return
  }
  router.push({
    path: '/ticket-checkout',
    query: {
      attraction_id: String(detail.value.id),
      package_id: String(selectedPackage.value?.id || ''),
      package_selections: JSON.stringify(selectedPackages.value.map(item => ({
        package_id: item.id,
        quantity: item.quantity
      }))),
      visit_date: selectedVisitDate.value,
      transport_price_id: selectedTransportId.value ? String(selectedTransportId.value) : ''
    }
  })
}

function updateDesktopMode() {
  isDesktop.value = window.innerWidth >= 1024
}

function scrollToSection(section) {
  const map = {
    booking: bookingSectionRef.value,
    intro: introSectionRef.value,
    transport: transportSectionRef.value
  }
  activeAnchor.value = section
  map[section]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// 保存进入本页时的原始 title，离开时恢复
const _prevTitle = typeof document !== 'undefined' ? document.title : ''

// ===== 评价数据 =====
const reviewList = ref([])
const reviewStats = ref({ avg_rating: null, total: 0 })
const reviewLoading = ref(false)

async function loadReviews(attractionId) {
  reviewLoading.value = true
  try {
    const res = await getTicketReviews(attractionId, { page: 1, per_page: 10 })
    reviewList.value = res.data?.list || []
    reviewStats.value = {
      avg_rating: res.data?.avg_rating,
      total: res.data?.total || 0,
    }
  } catch (e) {
    // 评价拉不到不影响主流程，静默
    reviewList.value = []
    reviewStats.value = { avg_rating: null, total: 0 }
  } finally {
    reviewLoading.value = false
  }
}

function formatReviewDate(s) {
  if (!s) return ''
  const d = new Date(s)
  if (isNaN(d.getTime())) return ''
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadData() {
  loading.value = true
  try {
    const attractionId = route.params.id
    const [detailRes, transportRes] = await Promise.all([
      getTicketAttraction(attractionId),
      getTicketTransportOptions({ attraction_id: attractionId }).catch(() => ({ data: [] }))
    ])
    detail.value = detailRes.data
    // 写 title：浏览器 tab 显示景点名 + WhatsApp 浮动按钮能读到
    if (detail.value?.name) {
      document.title = detail.value.name
    }
    packages.value = detailRes.data?.packages || []
    transportOptions.value = transportRes.data || []
    selectedTransportId.value = ''
    activePackageId.value = packages.value[0]?.id || null
    packages.value.forEach((item, index) => {
      packageQuantities[item.id] = index === 0 ? 1 : 0
    })
    activeImage.value = 0
    currentMonth.value = getMonthStart(today)
    ensureSelectedDateIsValid()

    // 异步加载评价（不阻塞主流程）
    loadReviews(attractionId)
  } catch (error) {
    showInlineNotice(error.message || t('common.noData'), 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', updateDesktopMode)
  loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateDesktopMode)
  if (ticketNoticeTimer) {
    clearTimeout(ticketNoticeTimer)
    ticketNoticeTimer = null
  }
  // 离开门票详情时恢复 title
  if (typeof document !== 'undefined' && _prevTitle) {
    document.title = _prevTitle
  }
})
</script>

<style scoped>
.ticket-detail-page {
  padding-top: 0;
  padding-bottom: 110px;
  background: #f8f4ee;
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.ticket-detail-desktop {
  padding-top: 12px;
}

.ticket-detail-desktop__hero {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 14px;
  margin-bottom: 12px;
}

.ticket-detail-desktop__gallery,
.ticket-detail-desktop__summary {
  margin: 0;
}

.ticket-detail-desktop__heading-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}

.detail-title--desktop {
  font-size: 24px;
  line-height: 1.18;
}

.detail-subtitle--desktop {
  margin-top: 8px;
  font-size: 13px;
}

.ticket-detail-desktop__city {
  font-size: 14px;
  color: #8f6b3d;
  font-weight: 700;
}

.meta-row--desktop {
  margin-top: 14px;
}

.meta-chip--featured {
  background: rgba(200, 169, 126, 0.16);
  color: #8f6b3d;
}

.ticket-detail-desktop__summary-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.ticket-detail-desktop__price-box {
  min-width: 128px;
  text-align: right;
}

.ticket-detail-desktop__price-label {
  font-size: 13px;
  color: #8d7b67;
}

.ticket-detail-desktop__price {
  margin-top: 4px;
  font-size: 32px;
  line-height: 1;
  font-weight: 700;
  color: var(--accent-dark);
}

.ticket-detail-desktop__info-grid {
  margin-top: 14px;
  display: grid;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid rgba(200, 169, 126, 0.18);
}

.ticket-detail-desktop__info-label {
  font-size: 13px;
  color: #8d7b67;
  margin-bottom: 6px;
}

.ticket-detail-desktop__info-value {
  font-size: 13px;
  line-height: 1.68;
  color: #4a3728;
}

.ticket-detail-desktop__map-links {
  display: inline-flex;
  gap: 8px;
  margin-left: 10px;
  flex-wrap: wrap;
  vertical-align: middle;
}

.ticket-detail-desktop__map-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(200, 169, 126, 0.14);
  color: var(--accent-dark);
  text-decoration: none;
  font-weight: 600;
  font-size: 12px;
}

.ticket-detail-desktop__map-link--secondary {
  background: rgba(74, 55, 40, 0.08);
  color: var(--text);
}

.ticket-detail-anchor-bar {
  display: flex;
  align-items: stretch;
  margin-bottom: 12px;
  border: 1px solid rgba(200, 169, 126, 0.22);
  background: rgba(200, 169, 126, 0.14);
  border-radius: 16px;
  overflow: hidden;
}

.ticket-detail-anchor-bar__item {
  min-width: 150px;
  height: 54px;
  border: none;
  background: transparent;
  color: #4a3728;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.ticket-detail-anchor-bar__item.active {
  background: rgba(255, 252, 247, 0.96);
  color: var(--accent-dark);
}

.gallery-section {
  margin: 12px;
  padding: 12px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.06);
}

.main-image-wrap {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  background: linear-gradient(180deg, #f7f8fa 0%, #eef2f6 100%);
  aspect-ratio: 16 / 10;
}

.main-image,
.image-placeholder {
  width: 100%;
  height: 100%;
}

.main-image {
  object-fit: cover;
  cursor: zoom-in;
}

.gallery-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  font-size: 26px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
  user-select: none;
}

.gallery-nav:hover {
  background: rgba(0, 0, 0, 0.65);
  transform: translateY(-50%) scale(1.05);
}

.gallery-nav--prev {
  left: 10px;
}

.gallery-nav--next {
  right: 10px;
}

.gallery-counter {
  position: absolute;
  right: 12px;
  bottom: 10px;
  z-index: 2;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  pointer-events: none;
}

@media (max-width: 768px) {
  .gallery-nav {
    width: 34px;
    height: 34px;
    font-size: 22px;
  }
  .gallery-nav--prev { left: 6px; }
  .gallery-nav--next { right: 6px; }
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: rgba(0, 0, 0, 0.15);
}

.thumbnail-list {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.thumbnail-item {
  flex: 0 0 68px;
  height: 68px;
  padding: 3px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: #f7f8fa;
}

.thumbnail-item.active {
  border-color: var(--accent);
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 9px;
}

.detail-body {
  display: block;
}

.transport-panel-card {
  overflow: hidden;
}

.transport-panel-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.transport-panel-card__title {
  margin-bottom: 0;
}

.transport-panel-card__subtitle {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: #7b6b5d;
}

.transport-panel-card__badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(200, 169, 126, 0.14);
  color: #8f6b3d;
  font-size: 13px;
  font-weight: 700;
}

.detail-main,
.detail-sidebar {
  min-width: 0;
}

.intro-card,
.info-card,
.package-card,
.calendar-card,
.transport-card,
.rules-card,
.booking-summary-card {
  margin-top: 12px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.detail-title {
  margin: 0;
  font-size: 22px;
  line-height: 1.35;
  color: #3b2b1f;
}

.detail-subtitle {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.7;
  color: #7b6b5d;
}

.meta-row {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-chip {
  padding: 4px 8px;
  border-radius: 999px;
  background: #f4eadb;
  color: #8a6635;
  font-size: 11px;
}

.price-box {
  margin-top: 14px;
}

.price-label {
  font-size: 12px;
  color: #9a8c7f;
}

.price-value {
  margin-top: 4px;
  font-size: 28px;
  font-weight: 700;
  color: #b98745;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #3b2b1f;
  margin-bottom: 12px;
}

.package-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.package-card-title {
  margin-bottom: 0;
}

.ticket-cart-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 90px;
  height: 38px;
  padding: 0 14px;
  border: 1px solid #eadfce;
  border-radius: 999px;
  background: #fff;
  color: #3b2b1f;
  font-size: 14px;
  font-weight: 600;
}

.ticket-cart-badge {
  margin-left: 6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ff6b35;
  color: #fff;
  font-size: 11px;
  line-height: 18px;
  text-align: center;
}

.info-item + .info-item {
  margin-top: 12px;
}

.info-label {
  font-size: 12px;
  color: #8d7b67;
}

.info-value {
  margin-top: 4px;
  font-size: 14px;
  line-height: 1.8;
  color: #4a3728;
}

.multiline,
.rule-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.package-list,
.transport-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transport-list--inline {
  margin-bottom: 10px;
}

.package-list--horizontal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
}

.package-item,
.transport-item {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #ece6dd;
  background: #fffdf9;
}

.package-item {
  cursor: pointer;
}

.package-item--horizontal {
  width: 100%;
  min-width: 0;
}

.package-item.active,
.transport-item.active {
  border-color: #c69a62;
  background: #fff7ee;
}

.package-main,
.transport-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.package-main--horizontal {
  align-items: flex-start;
}

.package-copy {
  min-width: 0;
  flex: 1;
}

.package-name,
.transport-name {
  font-size: 15px;
  font-weight: 700;
  color: #3b2b1f;
}

.package-type,
.transport-desc {
  margin-top: 4px;
  font-size: 12px;
  color: #8d7b67;
}

.package-price {
  font-size: 20px;
  font-weight: 700;
  color: #b98745;
  text-align: right;
}

.package-original {
  margin-top: 4px;
  font-size: 12px;
  color: #aaa094;
  text-decoration: line-through;
  text-align: right;
}

.package-note {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.7;
  color: #7b6b5d;
}

.package-detail-toggle-row {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.package-detail-toggle {
  border: none;
  background: transparent;
  color: #c69a62;
  font-size: 13px;
  font-weight: 600;
}

.package-detail-panel {
  margin-top: 8px;
  padding: 12px;
  border: 1px solid #efe4d4;
  border-radius: 12px;
  background: rgba(255,255,255,0.72);
}

.package-quantity-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.package-quantity-label {
  font-size: 12px;
  color: #8d7b67;
}

.qty-stepper {
  display: inline-flex;
  align-items: center;
  border: 1px solid #e6dccd;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}

.qty-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #fff;
  color: #3b2b1f;
  font-size: 22px;
}

.qty-btn:disabled {
  opacity: 0.35;
}

.qty-value {
  min-width: 42px;
  text-align: center;
  font-size: 15px;
  font-weight: 700;
  color: #3b2b1f;
}

.desktop-package-card {
  overflow: hidden;
}

.calendar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.calendar-selected-label {
  font-size: 12px;
  color: #8d7b67;
}

.calendar-selected-value {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 700;
  color: #3b2b1f;
}

.calendar-month-switch {
  display: flex;
  align-items: center;
  gap: 10px;
}

.month-btn {
  width: 34px;
  height: 34px;
  border: 1px solid #eadfce;
  border-radius: 999px;
  background: #fff;
  color: #6e5a42;
  font-size: 20px;
}

.month-btn:disabled {
  cursor: not-allowed;
  opacity: 0.38;
}

.month-title {
  min-width: 64px;
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  color: #3b2b1f;
}

.booking-window-tip {
  margin-bottom: 12px;
  font-size: 12px;
  color: #8d7b67;
}

.booking-window-tip--transfer {
  margin-bottom: 10px;
  line-height: 1.6;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  margin-bottom: 10px;
  color: #666;
  font-size: 13px;
  text-align: center;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.calendar-day {
  position: relative;
  min-height: 72px;
  border: 1px solid #efe4d4;
  border-radius: 16px;
  background: #fff;
  padding: 8px 4px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.calendar-day.empty {
  visibility: hidden;
}

.calendar-day.disabled {
  opacity: 0.36;
  background: #faf7f2;
}

.calendar-day.selected {
  border-color: #2e2a24;
  box-shadow: inset 0 0 0 1px #2e2a24;
}

.calendar-day.today .day-number {
  color: #c69a62;
}

.day-tag {
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 10px;
  color: #9b8a73;
}

.day-number {
  font-size: 16px;
  font-weight: 700;
  color: #1f1f1f;
}

.day-price {
  margin-top: 6px;
  font-size: 11px;
  color: #8d7b67;
}

.transport-price {
  font-size: 18px;
  font-weight: 700;
  color: #b98745;
}

.transport-hero-panel {
  margin: 12px 0 14px;
  padding: 16px 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 248, 238, 0.98) 0%, rgba(248, 239, 225, 0.98) 100%);
  border: 1px solid rgba(200, 169, 126, 0.28);
  box-shadow: 0 10px 24px rgba(110, 90, 66, 0.08);
}

.transport-hero-panel__eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #a07a48;
}

.transport-hero-panel__title {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 800;
  color: #3b2b1f;
}

.transport-hero-panel__desc {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: #7b6b5d;
}

.transport-empty-state {
  padding: 14px;
  border: 1px dashed #e3d7c6;
  border-radius: 14px;
  background: rgba(255, 252, 247, 0.88);
}

.transport-empty-state__title {
  font-size: 14px;
  font-weight: 700;
  color: #4a3728;
}

.transport-empty-state__desc {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.7;
  color: #8d7b67;
}

.transport-service-type-field {
  margin-bottom: 12px;
}

.transport-service-type-label {
  margin-bottom: 8px;
  font-size: 12px;
  color: #8d7b67;
}

.transport-service-type-select {
  width: 100%;
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid #e7d9c5;
  border-radius: 12px;
  background: #fff;
  color: #3b2b1f;
  font-size: 14px;
}

.ticket-transfer-vehicle-list {
  margin-top: 4px;
}

.ticket-transfer-vehicle-list--main {
  display: grid;
  gap: 14px;
}

.vehicle-card--transport {
  padding: 0;
  overflow: hidden;
}

.vehicle-card__top {
  display: flex;
  align-items: stretch;
  gap: 14px;
  width: 100%;
  padding: 14px;
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
  border: 2px solid #ece6dd;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  text-align: left;
}

.vehicle-card.active {
  border-color: #c69a62;
  background: #fff7ee;
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

.vehicle-icon--large {
  width: 196px;
  height: 132px;
  border-radius: 16px;
  box-shadow: inset 0 0 0 1px rgba(200, 169, 126, 0.18);
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
  color: #3b2b1f;
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
  color: #8d7b67;
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
  color: #8d7b67;
  margin-top: 8px;
}

.vehicle-thumb-row {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.vehicle-thumb {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(200, 169, 126, 0.28);
  background: #fff;
  flex: 0 0 auto;
  box-shadow: 0 4px 10px rgba(74, 55, 40, 0.08);
}

.vehicle-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.vehicle-side {
  min-width: 122px;
  text-align: right;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.vehicle-side--boxed {
  min-width: 168px;
  padding: 14px;
  border-radius: 16px;
  background: linear-gradient(180deg, #fffdf9 0%, #f8f1e6 100%);
  border: 1px solid rgba(200, 169, 126, 0.2);
}

.vehicle-side-select-label {
  font-size: 11px;
  color: #8d7b67;
}

.vehicle-service-select {
  width: 100%;
  min-width: 118px;
  margin-top: 6px;
  padding: 9px 12px;
  border: 1px solid #e3d7c6;
  border-radius: 12px;
  background: #fffdf9;
  color: #3b2b1f;
  font-size: 13px;
  font-weight: 600;
  outline: none;
}

.vehicle-price-label {
  font-size: 11px;
  color: #8d7b67;
}

.vehicle-price {
  margin-top: 4px;
  font-size: 18px;
  color: #b98745;
  font-weight: 700;
}

.vehicle-side-tip {
  margin-top: 6px;
  font-size: 11px;
  color: #8d7b67;
  line-height: 1.4;
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

.image-preview-title__text {
  font-size: 15px;
  font-weight: 700;
}

.image-preview-meta {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.image-preview-meta__chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(8px);
  font-size: 12px;
  color: #fff;
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

.booking-summary-card {
  background: linear-gradient(180deg, #fffdf8 0%, #f8f1e6 100%);
}

.booking-selected-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.booking-selected-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(110, 90, 66, 0.16);
}

.booking-selected-item:last-child {
  border-bottom: none;
}

.booking-selected-name {
  font-size: 14px;
  font-weight: 700;
  color: #3b2b1f;
}

.booking-selected-count {
  margin-top: 4px;
  font-size: 12px;
  color: #8d7b67;
}

.booking-selected-subtotal {
  font-size: 15px;
  font-weight: 700;
  color: #b98745;
}

.booking-summary__meta {
  font-size: 12px;
  color: #8d7b67;
}

.booking-summary__title {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 700;
  color: #3b2b1f;
}

.booking-summary__date {
  margin-top: 6px;
  font-size: 13px;
  color: #8d7b67;
}

.booking-summary__qty {
  margin-top: 8px;
  font-size: 13px;
  color: #6e5a42;
}

.booking-summary__price {
  margin: 14px 0;
  font-size: 30px;
  line-height: 1;
  font-weight: 700;
  color: var(--accent-dark);
}

.booking-summary__transfer {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.6;
  color: #6e5a42;
}

.booking-summary__actions {
  display: grid;
  gap: 10px;
}

.ticket-inline-notice-fade-enter-active,
.ticket-inline-notice-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.ticket-inline-notice-fade-enter-from,
.ticket-inline-notice-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 10px);
}

.ticket-inline-notice {
  position: fixed;
  left: 50%;
  bottom: 96px;
  transform: translateX(-50%);
  z-index: 60;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  max-width: calc(100vw - 32px);
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(33, 33, 33, 0.92);
  color: #fff;
  font-size: 13px;
  line-height: 1.3;
  text-align: center;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.18);
}

.ticket-inline-notice--success,
.ticket-inline-notice--error,
.ticket-inline-notice--info {
  background: rgba(33, 33, 33, 0.92);
}

/* ===== 用户评价区 ===== */
.ticket-reviews-card {
  margin: 12px;
  margin-bottom: 100px;   /* 给底部 bottom-action 留空间 */
  padding: 16px 18px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.06);
}
.ticket-reviews-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f4ebe0;
}
.ticket-reviews-card__title {
  font-size: 16px;
  font-weight: 700;
  color: #3b2b1f;
  margin: 0;
}
.ticket-reviews-card__stat {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.ticket-reviews-card__avg {
  font-size: 18px;
  font-weight: 700;
  color: #ff9800;
}
.ticket-reviews-card__count {
  font-size: 12px;
  color: #8d7b67;
}
.ticket-reviews-card__loading {
  text-align: center;
  padding: 24px 0;
}
.ticket-reviews-card__empty {
  padding: 24px 0;
  text-align: center;
  font-size: 13px;
  color: #aaa;
}
.ticket-review-item {
  padding: 12px 0;
  border-bottom: 1px solid #f7f0e6;
}
.ticket-review-item:last-child {
  border-bottom: none;
}
.ticket-review-item__head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}
.ticket-review-item__name {
  font-size: 13px;
  font-weight: 600;
  color: #4a3728;
}
.ticket-review-item__date {
  font-size: 12px;
  color: #aaa;
}
.ticket-review-item__comment {
  font-size: 13px;
  line-height: 1.6;
  color: #5a4a3a;
  white-space: pre-wrap;
}
.ticket-review-item__reply {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #fff7e6;
  font-size: 12px;
  line-height: 1.5;
  color: #8a6635;
}
.ticket-review-item__reply-label {
  font-weight: 600;
}

/* 桌面端：评价卡片 max-width，不要太宽 */
@media (min-width: 1024px) {
  .ticket-reviews-card {
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 32px;
  }
}

.bottom-action {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom));
  background: rgba(255,255,255,0.96);
  border-top: 1px solid rgba(0,0,0,0.06);
  backdrop-filter: blur(10px);
}

.mobile-bottom-action__buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bottom-action__label {
  font-size: 12px;
  color: #8d7b67;
}

.bottom-action__value {
  margin-top: 4px;
  font-size: 14px;
  color: #3b2b1f;
  font-weight: 700;
}

.bottom-action__date {
  margin-top: 4px;
  font-size: 12px;
  color: #8d7b67;
}

@media (min-width: 1024px) {
  .ticket-detail-page {
    padding-bottom: 36px;
    background: linear-gradient(180deg, #f7f2ea 0%, #f3ece0 100%);
  }

  .detail-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 320px;
    gap: 10px;
    align-items: start;
  }

  .detail-sidebar {
    position: sticky;
    top: calc(var(--nav-height) + 16px);
  }

  .detail-main {
    display: grid;
    gap: 12px;
  }

  .booking-card:first-child {
    margin-top: 0;
  }

  .calendar-card {
    margin-top: 0;
  }

  .info-card--desktop,
  .traffic-guide-card,
  .rules-card,
  .package-card {
    margin-top: 0;
  }

  .card-title--desktop {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .info-value--desktop,
  .rule-text {
    font-size: 13px;
    line-height: 1.75;
  }

  .traffic-guide-card__layout {
    display: block;
  }

  .traffic-guide-card__map {
    min-height: 220px;
    padding: 16px;
    border-radius: 14px;
    background: linear-gradient(135deg, #faf6f0 0%, #f2e8dc 100%);
    border: 1px solid rgba(200, 169, 126, 0.18);
  }

  .traffic-guide-card__map-title {
    font-size: 16px;
    font-weight: 700;
    color: #302417;
  }

  .traffic-guide-card__map-address {
    margin-top: 8px;
    font-size: 14px;
    line-height: 1.7;
    color: #4a3728;
  }

  .traffic-guide-card__map-hours {
    margin-top: 12px;
    font-size: 13px;
    line-height: 1.7;
    color: #6f5f50;
  }

  .traffic-guide-card__map-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 14px;
  }

  .traffic-guide-card__map-link {
    display: inline-flex;
    padding: 9px 16px;
    border-radius: 999px;
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 8px 18px rgba(200,169,126,0.2);
  }

  .traffic-guide-card__map-link--secondary {
    background: rgba(74, 55, 40, 0.82);
    box-shadow: 0 8px 18px rgba(74,55,40,0.14);
  }

  .traffic-guide-card__map--full {
    min-height: 0;
  }

  .mobile-bottom-action {
    display: none;
  }

  .ticket-inline-notice {
    bottom: 36px;
  }
}

@media (max-width: 1023px) {
  .transport-panel-card__head {
    flex-direction: column;
    align-items: stretch;
  }

  .transport-panel-card__badge {
    align-self: flex-start;
  }

  .transport-hero-panel {
    padding: 14px;
  }

  .transport-hero-panel__title {
    font-size: 18px;
  }

  .vehicle-card__top {
    flex-direction: column;
  }

  .vehicle-icon,
  .vehicle-icon--large {
    width: 100%;
    height: 180px;
  }

  .vehicle-side {
    width: 100%;
    min-width: 0;
    align-items: stretch;
    text-align: left;
  }

  .vehicle-service-select {
    width: 100%;
  }

  .desktop-package-card {
    margin-top: 12px;
  }

  .package-list--horizontal {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .package-item--horizontal {
    width: 100%;
  }

  .booking-summary-card {
    display: none;
  }
}
</style>
