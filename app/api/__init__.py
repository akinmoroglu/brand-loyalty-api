from fastapi import APIRouter
from app.api import brands, balances, transactions, provisions, customers

api_router = APIRouter()

api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(balances.router, tags=["balances"])
api_router.include_router(transactions.router, tags=["transactions"])
api_router.include_router(provisions.router, tags=["provisions"])
