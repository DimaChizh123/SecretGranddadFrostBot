from app.handlers.common import router as common_router
from app.handlers.create_room import router as create_room_router
from app.handlers.join_room import router as join_room_router
from app.handlers.admin import router as admin_router

routers = [common_router, create_room_router, join_room_router, admin_router]