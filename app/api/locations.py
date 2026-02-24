from flask import request
from app.api import api_bp
from app.models import Location
from app.utils import success_response, error_response, get_lang


@api_bp.route('/locations', methods=['GET'])
def get_locations():
    """获取民宿点列表"""
    lang = get_lang()
    
    locations = Location.query.filter_by(status=1)\
        .order_by(Location.sort_order.desc())\
        .all()
    
    return success_response([loc.to_dict(lang) for loc in locations])


@api_bp.route('/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """获取民宿点详情"""
    lang = get_lang()
    
    location = Location.query.filter_by(id=location_id, status=1).first()
    
    if not location:
        return error_response('民宿点不存在', 404)
    
    return success_response(location.to_dict(lang))


# 上海各区列表（用于自定义地址选择）
SHANGHAI_DISTRICTS = [
    {'value': '黄浦区', 'label_zh': '黄浦区', 'label_en': 'Huangpu', 'label_ru': 'Хуанпу', 'label_es': 'Huangpu'},
    {'value': '徐汇区', 'label_zh': '徐汇区', 'label_en': 'Xuhui', 'label_ru': 'Сюйхуэй', 'label_es': 'Xuhui'},
    {'value': '长宁区', 'label_zh': '长宁区', 'label_en': 'Changning', 'label_ru': 'Чаннин', 'label_es': 'Changning'},
    {'value': '静安区', 'label_zh': '静安区', 'label_en': 'Jingan', 'label_ru': 'Цзинъань', 'label_es': 'Jing\'an'},
    {'value': '普陀区', 'label_zh': '普陀区', 'label_en': 'Putuo', 'label_ru': 'Путо', 'label_es': 'Putuo'},
    {'value': '虹口区', 'label_zh': '虹口区', 'label_en': 'Hongkou', 'label_ru': 'Хункоу', 'label_es': 'Hongkou'},
    {'value': '杨浦区', 'label_zh': '杨浦区', 'label_en': 'Yangpu', 'label_ru': 'Янпу', 'label_es': 'Yangpu'},
    {'value': '闵行区', 'label_zh': '闵行区', 'label_en': 'Minhang', 'label_ru': 'Миньхан', 'label_es': 'Minhang'},
    {'value': '宝山区', 'label_zh': '宝山区', 'label_en': 'Baoshan', 'label_ru': 'Баошань', 'label_es': 'Baoshan'},
    {'value': '嘉定区', 'label_zh': '嘉定区', 'label_en': 'Jiading', 'label_ru': 'Цзядин', 'label_es': 'Jiading'},
    {'value': '浦东新区', 'label_zh': '浦东新区', 'label_en': 'Pudong', 'label_ru': 'Пудун', 'label_es': 'Pudong'},
    {'value': '金山区', 'label_zh': '金山区', 'label_en': 'Jinshan', 'label_ru': 'Цзиньшань', 'label_es': 'Jinshan'},
    {'value': '松江区', 'label_zh': '松江区', 'label_en': 'Songjiang', 'label_ru': 'Сунцзян', 'label_es': 'Songjiang'},
    {'value': '青浦区', 'label_zh': '青浦区', 'label_en': 'Qingpu', 'label_ru': 'Цинпу', 'label_es': 'Qingpu'},
    {'value': '奉贤区', 'label_zh': '奉贤区', 'label_en': 'Fengxian', 'label_ru': 'Фэнсянь', 'label_es': 'Fengxian'},
    {'value': '崇明区', 'label_zh': '崇明区', 'label_en': 'Chongming', 'label_ru': 'Чунмин', 'label_es': 'Chongming'},
]


@api_bp.route('/districts', methods=['GET'])
def get_districts():
    """获取上海各区列表"""
    lang = get_lang()

    districts = []
    for d in SHANGHAI_DISTRICTS:
        label = d.get(f'label_{lang}') or d['label_en'] or d['label_zh']
        districts.append({
            'value': d['value'],
            'label': label
        })

    return success_response(districts)
