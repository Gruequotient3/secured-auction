from fastapi import FastAPI
from server.routers import auth, add_balance, create_auction


app = FastAPI()

app.include_router(auth.router)
app.include_router(add_balance.router)
app.include_router(create_auction.router)

