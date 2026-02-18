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
    {'value': '黄浦区', 'label_zh': '黄浦区', 'label_en': 'Huangpu'},
    {'value': '徐汇区', 'label_zh': '徐汇区', 'label_en': 'Xuhui'},
    {'value': '长宁区', 'label_zh': '长宁区', 'label_en': 'Changning'},
    {'value': '静安区', 'label_zh': '静安区', 'label_en': 'Jingan'},
    {'value': '普陀区', 'label_zh': '普陀区', 'label_en': 'Putuo'},
    {'value': '虹口区', 'label_zh': '虹口区', 'label_en': 'Hongkou'},
    {'value': '杨浦区', 'label_zh': '杨浦区', 'label_en': 'Yangpu'},
    {'value': '闵行区', 'label_zh': '闵行区', 'label_en': 'Minhang'},
    {'value': '宝山区', 'label_zh': '宝山区', 'label_en': 'Baoshan'},
    {'value': '嘉定区', 'label_zh': '嘉定区', 'label_en': 'Jiading'},
    {'value': '浦东新区', 'label_zh': '浦东新区', 'label_en': 'Pudong'},
    {'value': '金山区', 'label_zh': '金山区', 'label_en': 'Jinshan'},
    {'value': '松江区', 'label_zh': '松江区', 'label_en': 'Songjiang'},
    {'value': '青浦区', 'label_zh': '青浦区', 'label_en': 'Qingpu'},
    {'value': '奉贤区', 'label_zh': '奉贤区', 'label_en': 'Fengxian'},
    {'value': '崇明区', 'label_zh': '崇明区', 'label_en': 'Chongming'},
]


@api_bp.route('/districts', methods=['GET'])
def get_districts():
    """获取上海各区列表"""
    lang = get_lang()
    
    districts = []
    for d in SHANGHAI_DISTRICTS:
        districts.append({
            'value': d['value'],
            'label': d['label_en'] if lang == 'en' else d['label_zh']
        })
    
    return success_response(districts)
