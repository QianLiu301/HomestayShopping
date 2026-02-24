"""
Translation dictionary for auto-filling Russian and Spanish translations.
Used by admin API endpoints and migration scripts.
"""

# Key: English (lowercase) -> (Russian, Spanish)
TRANSLATION_DICT = {
    # --- Vehicle types ---
    'economy': ('Эконом', 'Económico'),
    'economy sedan': ('Эконом седан', 'Sedán económico'),
    'comfort': ('Комфорт', 'Confort'),
    'comfort sedan': ('Комфорт седан', 'Sedán confort'),
    'business': ('Бизнес', 'Negocios'),
    'business sedan': ('Бизнес седан', 'Sedán de negocios'),
    'luxury': ('Люкс', 'Lujo'),
    'luxury sedan': ('Люкс седан', 'Sedán de lujo'),
    'suv': ('Внедорожник', 'SUV'),
    'luxury suv': ('Люкс внедорожник', 'SUV de lujo'),
    'van': ('Минивэн', 'Furgoneta'),
    'minivan': ('Минивэн', 'Minivan'),
    'mpv': ('Минивэн', 'Monovolumen'),
    'bus': ('Автобус', 'Autobús'),
    'minibus': ('Микроавтобус', 'Microbús'),
    'buick gl8': ('Бьюик GL8', 'Buick GL8'),
    'toyota alphard': ('Тойота Альфард', 'Toyota Alphard'),
    'mercedes-benz': ('Мерседес-Бенц', 'Mercedes-Benz'),
    'bmw': ('БМВ', 'BMW'),
    'audi': ('Ауди', 'Audi'),
    'tesla': ('Тесла', 'Tesla'),

    # --- Category names ---
    'snacks': ('Закуски', 'Aperitivos'),
    'drinks': ('Напитки', 'Bebidas'),
    'beverages': ('Напитки', 'Bebidas'),
    'fruit': ('Фрукты', 'Frutas'),
    'fruits': ('Фрукты', 'Frutas'),
    'fresh fruit': ('Свежие фрукты', 'Frutas frescas'),
    'daily necessities': ('Товары первой необходимости', 'Artículos de primera necesidad'),
    'daily supplies': ('Товары первой необходимости', 'Artículos de primera necesidad'),
    'toiletries': ('Средства гигиены', 'Artículos de aseo'),
    'instant food': ('Полуфабрикаты', 'Comida instantánea'),
    'instant noodles': ('Лапша быстрого приготовления', 'Fideos instantáneos'),
    'convenience food': ('Полуфабрикаты', 'Comida preparada'),
    'food': ('Еда', 'Comida'),
    'breakfast': ('Завтрак', 'Desayuno'),
    'lunch box': ('Обед', 'Almuerzo'),
    'dinner': ('Ужин', 'Cena'),
    'household': ('Бытовые товары', 'Artículos del hogar'),
    'household items': ('Бытовые товары', 'Artículos del hogar'),
    'personal care': ('Личная гигиена', 'Cuidado personal'),
    'medicine': ('Лекарства', 'Medicamentos'),
    'electronics': ('Электроника', 'Electrónica'),
    'souvenirs': ('Сувениры', 'Recuerdos'),
    'local specialties': ('Местные деликатесы', 'Especialidades locales'),
    'specialty': ('Специальные товары', 'Especialidades'),
    'other': ('Другое', 'Otros'),
    'others': ('Другое', 'Otros'),

    # --- Common product names ---
    'mineral water': ('Минеральная вода', 'Agua mineral'),
    'bottled water': ('Бутилированная вода', 'Agua embotellada'),
    'water': ('Вода', 'Agua'),
    'coca cola': ('Кока-Кола', 'Coca Cola'),
    'coca-cola': ('Кока-Кола', 'Coca Cola'),
    'coke': ('Кока-Кола', 'Coca Cola'),
    'sprite': ('Спрайт', 'Sprite'),
    'pepsi': ('Пепси', 'Pepsi'),
    'fanta': ('Фанта', 'Fanta'),
    'orange juice': ('Апельсиновый сок', 'Zumo de naranja'),
    'apple juice': ('Яблочный сок', 'Zumo de manzana'),
    'juice': ('Сок', 'Zumo'),
    'beer': ('Пиво', 'Cerveza'),
    'tsingtao beer': ('Пиво Циндао', 'Cerveza Tsingtao'),
    'green tea': ('Зелёный чай', 'Té verde'),
    'black tea': ('Чёрный чай', 'Té negro'),
    'tea': ('Чай', 'Té'),
    'coffee': ('Кофе', 'Café'),
    'instant coffee': ('Растворимый кофе', 'Café instantáneo'),
    'milk': ('Молоко', 'Leche'),
    'yogurt': ('Йогурт', 'Yogur'),
    'soy milk': ('Соевое молоко', 'Leche de soja'),
    'rice': ('Рис', 'Arroz'),
    'noodles': ('Лапша', 'Fideos'),
    'bread': ('Хлеб', 'Pan'),
    'cake': ('Торт', 'Pastel'),
    'cookies': ('Печенье', 'Galletas'),
    'biscuits': ('Печенье', 'Galletas'),
    'chocolate': ('Шоколад', 'Chocolate'),
    'chips': ('Чипсы', 'Patatas fritas'),
    'potato chips': ('Картофельные чипсы', 'Patatas fritas'),
    'candy': ('Конфеты', 'Caramelos'),
    'gum': ('Жвачка', 'Chicle'),
    'chewing gum': ('Жевательная резинка', 'Chicle'),
    'nuts': ('Орехи', 'Frutos secos'),
    'dried fruit': ('Сухофрукты', 'Frutas secas'),
    'apple': ('Яблоко', 'Manzana'),
    'banana': ('Банан', 'Plátano'),
    'orange': ('Апельсин', 'Naranja'),
    'grape': ('Виноград', 'Uva'),
    'grapes': ('Виноград', 'Uvas'),
    'watermelon': ('Арбуз', 'Sandía'),
    'mango': ('Манго', 'Mango'),
    'strawberry': ('Клубника', 'Fresa'),
    'peach': ('Персик', 'Melocotón'),
    'pear': ('Груша', 'Pera'),
    'toothbrush': ('Зубная щётка', 'Cepillo de dientes'),
    'toothpaste': ('Зубная паста', 'Pasta de dientes'),
    'shampoo': ('Шампунь', 'Champú'),
    'soap': ('Мыло', 'Jabón'),
    'towel': ('Полотенце', 'Toalla'),
    'tissue': ('Салфетки', 'Pañuelos'),
    'tissues': ('Салфетки', 'Pañuelos'),
    'toilet paper': ('Туалетная бумага', 'Papel higiénico'),
    'slippers': ('Тапочки', 'Zapatillas'),
    'umbrella': ('Зонт', 'Paraguas'),
    'raincoat': ('Дождевик', 'Impermeable'),
    'mosquito repellent': ('Средство от комаров', 'Repelente de mosquitos'),
    'sunscreen': ('Солнцезащитный крем', 'Protector solar'),
    'band-aid': ('Пластырь', 'Tiritas'),
    'bandage': ('Бинт', 'Vendaje'),
    'mask': ('Маска', 'Mascarilla'),
    'face mask': ('Маска для лица', 'Mascarilla facial'),
    'charger': ('Зарядное устройство', 'Cargador'),
    'phone charger': ('Зарядка для телефона', 'Cargador de teléfono'),
    'adapter': ('Адаптер', 'Adaptador'),
    'power adapter': ('Адаптер питания', 'Adaptador de corriente'),
    'sim card': ('SIM-карта', 'Tarjeta SIM'),
    'laundry detergent': ('Стиральный порошок', 'Detergente para ropa'),
    'cup noodles': ('Лапша быстрого приготовления', 'Fideos instantáneos en vaso'),
    'instant noodle': ('Лапша быстрого приготовления', 'Fideos instantáneos'),
    'egg': ('Яйцо', 'Huevo'),
    'eggs': ('Яйца', 'Huevos'),
    'ham': ('Ветчина', 'Jamón'),
    'sausage': ('Колбаса', 'Salchicha'),
    'ice cream': ('Мороженое', 'Helado'),
    'popsicle': ('Фруктовый лёд', 'Polo'),
    'dumpling': ('Пельмени', 'Dumplings'),
    'dumplings': ('Пельмени', 'Dumplings'),
    'frozen dumplings': ('Замороженные пельмени', 'Dumplings congelados'),
    'steamed bun': ('Паровая булочка', 'Bollo al vapor'),
    'steamed buns': ('Паровые булочки', 'Bollos al vapor'),
    'soy sauce': ('Соевый соус', 'Salsa de soja'),
    'vinegar': ('Уксус', 'Vinagre'),
    'oil': ('Масло', 'Aceite'),
    'cooking oil': ('Растительное масло', 'Aceite de cocina'),
    'salt': ('Соль', 'Sal'),
    'sugar': ('Сахар', 'Azúcar'),
    'seasoning': ('Приправы', 'Condimentos'),
    'spice': ('Специи', 'Especias'),
    'spices': ('Специи', 'Especias'),

    # --- Vehicle / product descriptions ---
    'suitable for 1-2 people': ('Подходит для 1-2 человек', 'Adecuado para 1-2 personas'),
    'suitable for 1-3 people': ('Подходит для 1-3 человек', 'Adecuado para 1-3 personas'),
    'suitable for 1-4 people': ('Подходит для 1-4 человек', 'Adecuado para 1-4 personas'),
    'suitable for 3-4 people': ('Подходит для 3-4 человек', 'Adecuado para 3-4 personas'),
    'suitable for 4-6 people': ('Подходит для 4-6 человек', 'Adecuado para 4-6 personas'),
    'suitable for 5-6 people': ('Подходит для 5-6 человек', 'Adecuado para 5-6 personas'),
    'suitable for 5-7 people': ('Подходит для 5-7 человек', 'Adecuado para 5-7 personas'),
    'suitable for 6-7 people': ('Подходит для 6-7 человек', 'Adecuado para 6-7 personas'),
    'suitable for families': ('Подходит для семей', 'Adecuado para familias'),
    'suitable for groups': ('Подходит для групп', 'Adecuado para grupos'),
    'suitable for business': ('Подходит для деловых поездок', 'Adecuado para viajes de negocios'),
    'spacious and comfortable': ('Просторный и комфортный', 'Espacioso y cómodo'),
    'large luggage space': ('Большое багажное отделение', 'Gran espacio para equipaje'),
    'economical choice': ('Экономичный выбор', 'Opción económica'),
    'comfortable ride': ('Комфортная поездка', 'Viaje cómodo'),
    'premium service': ('Премиум сервис', 'Servicio premium'),
    'luxury experience': ('Люкс опыт', 'Experiencia de lujo'),
    'best value': ('Лучшее соотношение цена/качество', 'Mejor relación calidad-precio'),
    'most popular': ('Самый популярный', 'Más popular'),
    'recommended': ('Рекомендуемый', 'Recomendado'),
    'standard sedan': ('Стандартный седан', 'Sedán estándar'),
    'comfortable sedan, suitable for 1-3 people': ('Комфортный седан, подходит для 1-3 человек', 'Sedán cómodo, adecuado para 1-3 personas'),
    'spacious suv, suitable for families': ('Просторный внедорожник, подходит для семей', 'SUV espacioso, adecuado para familias'),
    'business mpv, suitable for 4-6 people': ('Бизнес минивэн, подходит для 4-6 человек', 'Monovolumen de negocios, adecuado para 4-6 personas'),
    'luxury vehicle, premium service': ('Люкс автомобиль, премиум сервис', 'Vehículo de lujo, servicio premium'),
    'fresh': ('Свежий', 'Fresco'),
    'organic': ('Органический', 'Orgánico'),
    'imported': ('Импортный', 'Importado'),
    'local': ('Местный', 'Local'),
    'premium': ('Премиум', 'Premium'),
    'delicious': ('Вкусный', 'Delicioso'),
    'healthy': ('Здоровый', 'Saludable'),
    'natural': ('Натуральный', 'Natural'),
    'traditional': ('Традиционный', 'Tradicional'),
    'chinese style': ('Китайский стиль', 'Estilo chino'),
    'shanghai style': ('Шанхайский стиль', 'Estilo de Shanghái'),

    # --- Location-related ---
    'pudong airport': ('Аэропорт Пудун', 'Aeropuerto de Pudong'),
    'hongqiao airport': ('Аэропорт Хунцяо', 'Aeropuerto de Hongqiao'),
    'shanghai pudong international airport': ('Шанхайский международный аэропорт Пудун', 'Aeropuerto Internacional de Shanghái Pudong'),
    'shanghai hongqiao international airport': ('Шанхайский международный аэропорт Хунцяо', 'Aeropuerto Internacional de Shanghái Hongqiao'),
    'homestay': ('Гостевой дом', 'Casa de huéspedes'),
    'hotel': ('Гостиница', 'Hotel'),
    'apartment': ('Квартира', 'Apartamento'),
    'villa': ('Вилла', 'Villa'),
    'resort': ('Курорт', 'Resort'),
    'the bund': ('Набережная Бунд', 'El Bund'),
    'nanjing road': ('Нанкинская улица', 'Calle Nanjing'),
    "people's square": ('Народная площадь', 'Plaza del Pueblo'),
    'lujiazui': ('Луцзяцзуй', 'Lujiazui'),
    'french concession': ('Французская концессия', 'Concesión Francesa'),
    "jing'an temple": ('Храм Цзинъань', "Templo Jing'an"),
    'yu garden': ('Сад Юйюань', 'Jardín Yu'),
    'disneyland': ('Диснейленд', 'Disneyland'),
    'shanghai disneyland': ('Шанхайский Диснейленд', 'Disneyland de Shanghái'),
    'shanghai tower': ('Шанхайская башня', 'Torre de Shanghái'),
    'oriental pearl tower': ('Телебашня Восточная жемчужина', 'Torre de la Perla Oriental'),
    'zhujiajiao': ('Чжуцзяцзяо', 'Zhujiajiao'),
    'tianzifang': ('Тяньцзыфан', 'Tianzifang'),
    'xintiandi': ('Синьтяньди', 'Xintiandi'),
}


def lookup_translation(en_text):
    """
    Look up English text in the translation dictionary.
    Returns (russian, spanish) tuple or None if not found.
    """
    if not en_text:
        return None
    key = en_text.strip().lower()
    # Exact match
    if key in TRANSLATION_DICT:
        return TRANSLATION_DICT[key]
    # Partial match
    for dict_key, translations in TRANSLATION_DICT.items():
        if dict_key in key or key in dict_key:
            return translations
    return None


def auto_fill_translations(data, fields=None):
    """
    Auto-fill ru/es fields in request data based on English values.
    Only fills if the ru/es fields are not already provided.

    Args:
        data: dict of request data
        fields: list of field base names to translate (e.g., ['name', 'desc'])
                defaults to ['name', 'desc']

    Returns:
        Modified data dict with ru/es fields filled in.
    """
    if fields is None:
        fields = ['name', 'desc']

    for field in fields:
        en_val = data.get(f'{field}_en')
        if not en_val:
            continue

        result = lookup_translation(en_val)
        if result:
            ru_val, es_val = result
            if not data.get(f'{field}_ru'):
                data[f'{field}_ru'] = ru_val
            if not data.get(f'{field}_es'):
                data[f'{field}_es'] = es_val

    return data
