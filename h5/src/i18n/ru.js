export default {
  nav: { services: 'Услуги', shop: 'Магазин', howItWorks: 'Как это работает', orders: 'Заказы', contact: 'Контакты' },
  common: { home: 'Главная', shop: 'Магазин', cart: 'Корзина', orders: 'Заказы', transfer: 'Трансфер', submit: 'Отправить', confirm: 'Подтвердить', cancel: 'Отмена', loading: 'Загрузка...', noData: 'Нет данных', currency: '¥', back: 'Назад', all: 'Все', viewMore: 'Подробнее', required: 'Обязательно' },
  home: {
    heroLabel: 'Добро пожаловать',
    heroTitle: 'Откройте Шанхай, увезите воспоминания',
    heroSubtitle: 'Премиум сувениры с доставкой в номер и профессиональный трансфер',
    bookTransfer: 'Заказать трансфер', exploreShop: 'Открыть магазин', scrollDown: 'Прокрутите',
    servicesTitle: 'Трансфер из/в аэропорт', servicesSubtitle: 'Профессиональные водители, комфортные автомобили, пунктуальный сервис.',
    servicesComingSoon: 'Автомобили скоро появятся', bookNow: 'Забронировать',
    shopTitle: 'Коллекция подарков', shopSubtitle: 'Сувениры и местные специальности — заказ сегодня, доставка в номер до выезда.',
    productsComingSoon: 'Товары скоро появятся', viewAllProducts: 'Все товары',
    howLabel: 'Как это работает', howTitle: 'Простые шаги',
    step1Title: 'Выберите', step1Desc: 'Просмотрите коллекцию подарков или выберите трансфер.',
    step2Title: 'Закажите', step2Desc: 'Укажите номер комнаты и контактные данные.',
    step3Title: 'Доставка', step3Desc: 'Товары будут доставлены в номер до выезда.',
    step4Title: 'В путь', step4Desc: 'Возьмите сувениры и наслаждайтесь комфортной поездкой.',
    ordersTitle: 'Отследить заказ', ordersSubtitle: 'Введите номер заказа и контактные данные.',
    footerTagline: 'Делаем ваше пребывание в Шанхае незабываемым.', quickLinks: 'Быстрые ссылки'
  },
  shop: { title: 'Магазин подарков', search: 'Поиск товаров', allCategories: 'Все категории', addToCart: 'В корзину', buyNow: 'Купить', specs: 'Характеристики', desc: 'Описание', added: 'Добавлено в корзину' },
  cart: { title: 'Корзина', empty: 'Корзина пуста', goShop: 'За покупками', total: 'Итого', checkout: 'Оформить', delete: 'Удалить', selected: 'Выбрано: {count}' },
  transfer: { title: 'Трансфер', pickup: 'Встреча', dropoff: 'Проводы', combo: 'Встреча + Проводы', comboDiscount: 'Скидка {discount}% при заказе обоих', selectVehicle: 'Выбор автомобиля', seats: '{n} мест', luggage: '{n} багаж', extraPrice: '+¥{price}', noExtra: 'Без доплаты', flightNo: 'Номер рейса', flightTime: 'Время рейса', selectAddress: 'Выбрать адрес', homestayAddress: 'Адрес отеля', customAddress: 'Другой адрес', selectDistrict: 'Выбрать район', inputAddress: 'Введите адрес', contactInfo: 'Контакты', contactName: 'ФИО', contactPhone: 'Телефон', contactEmail: 'Электронная почта', remark: 'Примечание', remarkPlaceholder: 'Дополнительные пожелания', priceDetail: 'Детали цены', basePrice: 'Базовая цена', vehicleExtra: 'Доплата за авто', discount: 'Скидка', totalPrice: 'Итого', submitOrder: 'Оформить заказ' },
  checkout: { title: 'Подтверждение', address: 'Доставка', selectLocation: 'Выбрать отель', roomNumber: 'Номер комнаты', roomPlaceholder: 'Введите номер', contact: 'Контакты', coupon: 'Купон', couponPlaceholder: 'Введите код купона', verify: 'Проверить', couponValid: 'Купон применён, -¥{amount}', couponInvalid: 'Купон недействителен', payment: 'Способ оплаты', wechat: 'WeChat Pay', alipay: 'Alipay', creditCard: 'Банковская карта', orderItems: 'Товары', subtotal: 'Подытог', totalPrice: 'К оплате', placeOrder: 'Оформить заказ', phoneOrEmail: 'Укажите телефон или email', roomRequired: 'Укажите номер комнаты' },
  order: { success: 'Заказ оформлен', orderNo: 'Номер заказа', amount: 'Сумма', tips: 'Мы обработаем ваш заказ в ближайшее время.', backHome: 'На главную', continueShopping: 'Продолжить покупки', queryTitle: 'Поиск заказа', inputOrderNo: 'Введите номер заказа', inputContact: 'Телефон или email', query: 'Найти', status: 'Статус', statusMap: { 0: 'Ожидает', 1: 'Подтверждён', 2: 'В обработке', 3: 'Завершён', 4: 'Отменён' }, paymentStatus: { 0: 'Не оплачен', 1: 'Оплачен' }, type: { shop: 'Заказ из магазина', transfer: 'Заказ трансфера' } },
  payment: { title: 'Сканировать для оплаты', amountToPay: 'Сумма к оплате', scanTip: 'Отсканируйте QR-код выше с помощью телефона для оплаты', remarkTip: 'Укажите номер заказа в примечании к переводу', confirmPaid: 'Я оплатил', cancelOrder: 'Оплатить позже', qrNotSet: 'QR-код не настроен, свяжитесь с нами', paymentSubmitted: 'Подтверждение оплаты отправлено, ожидает проверки', confirmFailed: 'Ошибка сети. Ваш платёж зафиксирован, свяжитесь с нами для подтверждения.', nextStepProof: 'Я оплатил, далее', proofTitle: 'Подтверждение оплаты', proofSubtitle: 'Загрузите скриншот или введите номер транзакции (одно из двух)', uploadScreenshot: 'Загрузить скриншот', inputTxId: 'Номер транзакции', clickUpload: 'Нажмите для загрузки скриншота', txIdPlaceholder: 'Введите номер транзакции WeChat/Alipay', uploadFailed: 'Ошибка загрузки, попробуйте снова' },
  lang: { title: 'Язык', zh: '中文', en: 'English', ru: 'Русский', es: 'Español' }
}
