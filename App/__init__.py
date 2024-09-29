from flask import Flask

from .config import Config
from .exts import bcrypt, db
from App.exts import init_ext
from .views.found_items_view import found_items_bp
from .views.main_view import main_bp
from .models.user_model import *
from .models.communication_model import *
from .models.found_items_model import *
from .models.lost_items_model import *
from .models.forum_model import *
from .views.user_view import user_bp
from .models.faq_model import *
from .views.lost_items_view import *
from .views.user_dashboard_view import *
from .views.admin_dashboard_view import *
from .models.announce_model import *
from .views.announce_view import *


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # db_uri = 'mysql+pymysql://root:123456qian@localhost:3306/DCLostandFound'
    # app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SECRET_KEY'] = 'joisdjfds8fsd8f'
    # app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

    app.register_blueprint(main_bp)
    app.register_blueprint(found_items_bp,url_prefix='/found_items')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(lost_items_bp, url_prefix='/lost_items')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(announce_bp, url_prefix='/announcements')

    init_ext(app)

    return app


