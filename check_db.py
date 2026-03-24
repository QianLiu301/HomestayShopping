"""检查数据库中商品的 images 字段"""
from app import create_app, db
from app.models import Product

app = create_app()
with app.app_context():
    products = Product.query.order_by(Product.id.desc()).limit(10).all()
    print(f"{'ID':<5} {'名称':<20} {'images 字段'}")
    print("-" * 70)
    for p in products:
        name = p.name_zh or p.name_en or '?'
        print(f"{p.id:<5} {name:<20} {p.images}")
