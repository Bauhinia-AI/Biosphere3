from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
from flask import Flask, jsonify, request
from flask.views import MethodView
#For the sake of efficiency and simplicity we use fastapi :p.
#FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

app = FastAPI()

#Pydantic is a data validation library in Python. It enforces type hints at runtime, and provides user-friendly errors when data is invalid.
class MarketData(BaseModel):
    merchantid: str
    merchantprice: float
    merchantamount: int
    merchantcash: float
    merchantk: float


class CharacterStats(BaseModel):
    health: float
    energy: float
    knowledge: float
    fullness: float

class CharacterStatus(BaseModel):
    coordinate: str
    subject: str

class CharacterBasicInfo(BaseModel):
    userid: int
    jobid: int
    cash: float
    gender: str
    username: str

class MerchantItem(BaseModel):
    merchantid: str
    merchantnum: int


# simulate data
market_database = {
    "123": MarketData(merchantid="123", merchantprice=500.0, merchantamount=250, merchantcash=12500.0, merchantk=6250000.0),
    "456": MarketData(merchantid="456", merchantprice=150.0, merchantamount=600, merchantcash=9000.0, merchantk=5400000.0),
}

characters_data = [
    CharacterStats(health=100.0, energy=80.0, knowledge=90.0, fullness=70.0),
    CharacterStats(health=85.0, energy=75.0, knowledge=95.0, fullness=65.0)
]

characters_status = [
    CharacterStatus(coordinate="35.6895° N, 139.6917° E", subject="Exploring Tokyo"),
    CharacterStatus(coordinate="51.5074° N, 0.1278° W", subject="Visiting London")
]

characters_info = [
    CharacterBasicInfo(userid=1, jobid=101, cash=1500.0, gender="male", username="JohnDoe"),
    CharacterBasicInfo(userid=2, jobid=102, cash=1700.0, gender="female", username="JaneDoe")
]

inventory_items = [
    MerchantItem(merchantid="M001", merchantnum=10),
    MerchantItem(merchantid="M002", merchantnum=5)
]


# container for return data
class MarketResponse(BaseModel):
    merchant: List[MarketData]

class CharactersResponse(BaseModel):
    characters: List[CharacterStats]

class CharactersStatusResponse(BaseModel):
    characters: List[CharacterStatus]

class CharactersInfoResponse(BaseModel):
    characters: List[CharacterBasicInfo]

class InventoryResponse(BaseModel):
    items: List[MerchantItem]



@app.get("/trade")
async def get_market_data(merchantid: Optional[str] = None):
    if merchantid:
        market_info = market_database.get(merchantid)
        if not market_info:
            raise HTTPException(status_code=404, detail="Market data not found for given merchantid")
        return MarketResponse(merchant=[market_info])
    else:
        return MarketResponse(merchant=list(market_database.values()))
    
    
@app.get("/character/data")
async def get_character_stats():
    return CharactersResponse(characters=characters_data)

@app.get("/character/status")
async def get_character_status():
    return CharactersStatusResponse(characters=characters_status)

@app.get("/character/bsinfo")
async def get_character_basic_info():
    return CharactersInfoResponse(characters=characters_info)

@app.get("/character/inventory")
async def get_inventory():
    return InventoryResponse(items=inventory_items)


if __name__ == "__main__":
    #uvicorn is a lightning-fast ASGI server implementation, using uvloop and httptools.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)