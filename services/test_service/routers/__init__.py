from fastapi import APIRouter
from .tarriffs import router as prod_router


def register_routers(app):
    router = APIRouter(prefix='/api/v1')

    router.include_router(
        prod_router,
    )
    app.include_router(router)
    return app
