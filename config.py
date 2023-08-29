import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "khó mà đoán được é é"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(base_dir, "data.sqlite")}'
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:QK6Z7tJvNm69itY7KCtf@containers-us-west-109.railway.app:7484/railway"
    FLASKY_ADMIN = "lebaquoctrung@gmail.com"
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_FOLLOWERS_PER_PAGE = 10
    FLASKY_COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(base_dir, "data.sqlite")}'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(base_dir, "data.sqlite")}'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(base_dir, "data.sqlite")}'


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
