"""免费攻略 API：公开列表/详情 + 管理端 CRUD"""
from flask import request
from app.api import api_bp
from app.models import Guide, TicketAttraction
from app import db
from app.utils import success_response, error_response, admin_required, paginate_query, get_lang, escape_like
from app.translations import auto_fill_translations


# ==================== 公开接口 ====================

@api_bp.route('/guides', methods=['GET'])
def list_guides():
    lang = get_lang()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category = request.args.get('category', '').strip()

    query = Guide.query.filter(Guide.status == 1)
    if category:
        query = query.filter(Guide.category == category)
    query = query.order_by(Guide.sort_order.asc(), Guide.created_at.desc())

    result = paginate_query(query, page=page, per_page=per_page)
    items = []
    for g in result['items']:
        d = g.to_dict(lang)
        d.pop('content', None)
        d.pop('content_zh', None)
        d.pop('content_en', None)
        d.pop('content_ru', None)
        d.pop('content_es', None)
        items.append(d)

    return success_response({
        'list': items,
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'pages': result['pages'],
    })


@api_bp.route('/guides/<int:guide_id>', methods=['GET'])
def get_guide(guide_id):
    lang = get_lang()
    guide = Guide.query.get(guide_id)
    if not guide or guide.status != 1:
        return error_response('攻略不存在', 404)
    return success_response(guide.to_dict(lang))


# ==================== 管理端接口 ====================

@api_bp.route('/admin/guides', methods=['GET'])
@admin_required
def admin_list_guides():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status', '')
    category = request.args.get('category', '').strip()
    keyword = (request.args.get('keyword') or '').strip()

    query = Guide.query
    if status != '':
        try:
            query = query.filter(Guide.status == int(status))
        except (ValueError, TypeError):
            pass
    if category:
        query = query.filter(Guide.category == category)
    if keyword:
        like = f'%{escape_like(keyword)}%'
        query = query.filter(
            db.or_(
                Guide.title_zh.ilike(like),
                Guide.title_en.ilike(like),
                Guide.summary_zh.ilike(like),
                Guide.summary_en.ilike(like),
            )
        )
    query = query.order_by(Guide.sort_order.asc(), Guide.created_at.desc())

    result = paginate_query(query, page=page, per_page=per_page)
    return success_response({
        'list': [g.to_dict() for g in result['items']],
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'pages': result['pages'],
    })


@api_bp.route('/admin/guides', methods=['POST'])
@admin_required
def admin_create_guide():
    data = request.get_json() or {}
    data = auto_fill_translations(data, ['title', 'summary', 'content'])

    title_zh = data.get('title_zh') or data.get('title_en')
    title_en = data.get('title_en') or data.get('title_zh')
    if not title_zh and not title_en:
        return error_response('标题不能为空')

    attraction_id = data.get('attraction_id')
    if attraction_id:
        attraction = TicketAttraction.query.get(attraction_id)
        if not attraction:
            return error_response('关联景点不存在')

    images = data.get('images') or []
    cover_image = data.get('cover_image') or (images[0] if images else None)

    guide = Guide(
        title_zh=title_zh,
        title_en=title_en,
        title_ru=data.get('title_ru'),
        title_es=data.get('title_es'),
        summary_zh=data.get('summary_zh') or data.get('summary_en'),
        summary_en=data.get('summary_en') or data.get('summary_zh'),
        summary_ru=data.get('summary_ru'),
        summary_es=data.get('summary_es'),
        content_zh=data.get('content_zh') or data.get('content_en'),
        content_en=data.get('content_en') or data.get('content_zh'),
        content_ru=data.get('content_ru'),
        content_es=data.get('content_es'),
        cover_image=cover_image,
        images=images,
        category=data.get('category'),
        attraction_id=attraction_id or None,
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 1),
    )
    db.session.add(guide)
    db.session.commit()
    return success_response(guide.to_dict(), '创建成功')


@api_bp.route('/admin/guides/<int:guide_id>', methods=['PUT'])
@admin_required
def admin_update_guide(guide_id):
    guide = Guide.query.get(guide_id)
    if not guide:
        return error_response('攻略不存在', 404)

    data = request.get_json() or {}
    data = auto_fill_translations(data, ['title', 'summary', 'content'])

    if 'attraction_id' in data:
        aid = data['attraction_id']
        if aid:
            attraction = TicketAttraction.query.get(aid)
            if not attraction:
                return error_response('关联景点不存在')

    fields = [
        'title_zh', 'title_en', 'title_ru', 'title_es',
        'summary_zh', 'summary_en', 'summary_ru', 'summary_es',
        'content_zh', 'content_en', 'content_ru', 'content_es',
        'cover_image', 'images', 'category', 'attraction_id',
        'sort_order', 'status',
    ]
    for field in fields:
        if field in data:
            setattr(guide, field, data[field])

    if 'images' in data:
        images = data['images'] or []
        if images and not data.get('cover_image'):
            guide.cover_image = images[0]
        elif not images:
            guide.cover_image = None

    db.session.commit()
    return success_response(guide.to_dict(), '更新成功')


@api_bp.route('/admin/guides/<int:guide_id>', methods=['DELETE'])
@admin_required
def admin_delete_guide(guide_id):
    guide = Guide.query.get(guide_id)
    if not guide:
        return error_response('攻略不存在', 404)

    db.session.delete(guide)
    db.session.commit()
    return success_response(None, '删除成功')
