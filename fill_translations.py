"""
Fill Russian (ru) and Spanish (es) translations for all existing data.
Only updates records where the target language field is NULL/empty.

Usage: python fill_translations.py
"""
import os
from app import create_app, db
from app.models import Vehicle, Product, Category, Location
from app.translations import lookup_translation

app = create_app(os.getenv('FLASK_ENV', 'development'))


def fill_model_translations(model_class, name_field='name', desc_field=None):
    """Fill ru/es translations for a given model."""
    records = model_class.query.all()
    updated = 0

    for record in records:
        changed = False
        en_name = getattr(record, f'{name_field}_en', None)
        zh_name = getattr(record, f'{name_field}_zh', None)

        # Translate name
        result = lookup_translation(en_name)
        if result:
            ru_name, es_name = result
            if not getattr(record, f'{name_field}_ru', None):
                setattr(record, f'{name_field}_ru', ru_name)
                changed = True
            if not getattr(record, f'{name_field}_es', None):
                setattr(record, f'{name_field}_es', es_name)
                changed = True

        # Translate description if applicable
        if desc_field:
            en_desc = getattr(record, f'{desc_field}_en', None)
            desc_result = lookup_translation(en_desc)
            if desc_result:
                ru_desc, es_desc = desc_result
                if not getattr(record, f'{desc_field}_ru', None):
                    setattr(record, f'{desc_field}_ru', ru_desc)
                    changed = True
                if not getattr(record, f'{desc_field}_es', None):
                    setattr(record, f'{desc_field}_es', es_desc)
                    changed = True

        if changed:
            updated += 1
            display = en_name or zh_name
            ru_val = getattr(record, f'{name_field}_ru', None)
            es_val = getattr(record, f'{name_field}_es', None)
            print(f'  [{display}] -> ru: {ru_val}, es: {es_val}')

    return updated, len(records)


def fill_location_translations():
    """Fill ru/es translations for locations (name + address)."""
    records = Location.query.all()
    updated = 0

    for record in records:
        changed = False

        # Translate name
        result = lookup_translation(record.name_en)
        if result:
            if not record.name_ru:
                record.name_ru = result[0]
                changed = True
            if not record.name_es:
                record.name_es = result[1]
                changed = True

        # Translate address - try dictionary, else copy English
        if record.address_en:
            addr_result = lookup_translation(record.address_en)
            if addr_result:
                if not record.address_ru:
                    record.address_ru = addr_result[0]
                    changed = True
                if not record.address_es:
                    record.address_es = addr_result[1]
                    changed = True
            else:
                if not record.address_ru:
                    record.address_ru = record.address_en
                    changed = True
                if not record.address_es:
                    record.address_es = record.address_en
                    changed = True

        if changed:
            updated += 1
            print(f'  [{record.name_en or record.name_zh}]'
                  f' -> ru: {record.name_ru}, es: {record.name_es}')

    return updated, len(records)


with app.app_context():
    print('=' * 60)
    print('Filling Russian and Spanish translations...')
    print('=' * 60)

    print('\n--- Categories ---')
    u, t = fill_model_translations(Category)
    print(f'Updated {u}/{t} categories')

    print('\n--- Vehicles ---')
    u, t = fill_model_translations(Vehicle, desc_field='desc')
    print(f'Updated {u}/{t} vehicles')

    print('\n--- Products ---')
    u, t = fill_model_translations(Product, desc_field='desc')
    print(f'Updated {u}/{t} products')

    print('\n--- Locations ---')
    u, t = fill_location_translations()
    print(f'Updated {u}/{t} locations')

    db.session.commit()
    print('\n' + '=' * 60)
    print('All translations filled successfully!')
    print('=' * 60)
