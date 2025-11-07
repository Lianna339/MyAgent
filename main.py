import uvicorn
from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles
from config import settings
from utils import handler_error, cors, middlewares

from config.log_config import init_log
from api import routers
from utils.docs_oauth2 import MyOAuth2PasswordBearer

class Server:
    def __init__(self):
        init_log()
        my_oauth2 = MyOAuth2PasswordBearer(tokenUrl='/api/auth/', schema='JWT') # 加密认证
        self.app = FastAPI(dependencies=[Depends(my_oauth2)])
        self.app.mount('/static', StaticFiles(directory='static'), name='my_static')

    def init_app(self):
        handler_error.init_handler_errors(self.app)
        middlewares.init_middleware(self.app)
        cors.init_cors(self.app)
        routers.init_routers(self.app)

    def run(self):
        self.init_app()
        uvicorn.run(
            app=self.app,
            host=settings.HOST,
            port=settings.PORT
        )

if __name__=='__main__':
    Server().run()