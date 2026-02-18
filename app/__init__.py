from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import config

# 初始化扩展
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图（API路由）
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 健康检查路由
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Homestay API is running'}
    
    return app
