from flask import request
from app.api import api_bp
from app.models import Vehicle
from app.utils import success_response, error_response, get_lang


@api_bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """获取车型列表"""
    lang = get_lang()
    
    vehicles = Vehicle.query.filter_by(status=1)\
        .order_by(Vehicle.sort_order.desc())\
        .all()
    
    return success_response([v.to_dict(lang) for v in vehicles])


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """获取车型详情"""
    lang = get_lang()
    
    vehicle = Vehicle.query.filter_by(id=vehicle_id, status=1).first()
    
    if not vehicle:
        return error_response('车型不存在', 404)
    
    return success_response(vehicle.to_dict(lang))
