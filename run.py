import os
from app import create_app

# 获取环境配置
config_name = os.getenv('FLASK_ENV', 'development')

# 创建应用
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(config_name == 'development'))
