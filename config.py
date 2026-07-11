import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # 数据库配置 - Neon PostgreSQL (fallback to SQLite for local dev)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时
    
    # 跨域配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    # 私密文件（护照照片等）存储目录：不走静态文件服务，只能通过管理端鉴权接口访问
    PRIVATE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'private_uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB（支持视频上传）
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    # 视频格式仅管理端上传接口允许（攻略内容插入视频用）
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'webm', 'm4v'}


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
