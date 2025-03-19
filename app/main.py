import dotenv

dotenv.load_dotenv()


import uvicorn
import os
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from routers import status, users
from app.database.engine import create_db_and_tables
from urllib.parse import urlparse



app = FastAPI()
app.include_router(status.router)
app.include_router(users.router)
add_pagination(app)

if __name__ == "__main__":
    create_db_and_tables()
    app_url = urlparse(os.getenv('APP_URL'))
    uvicorn.run(app, host=app_url.hostname, port=app_url.port)