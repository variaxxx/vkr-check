from .auth.router import router as auth_router
from .documents.router import router as documents_router
from .report.router import router as report_router
from .user.router import router as user_router

routers = [documents_router, auth_router, user_router, report_router]
