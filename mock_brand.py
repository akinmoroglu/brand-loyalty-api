from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from datetime import timezone
from typing import Dict, Tuple, Optional
from fastapi.responses import JSONResponse

API_KEY = "test-secret"

app = FastAPI(title="Mock Brand Loyalty API", version="0.1.0")

# In-memory stores
balances: Dict[Tuple[str, str], int] = {}
provisions = {}  # key: provisionId, value: dict with brandId, userId, points, expiresAt
txns: Dict[str, Tuple[str, str, int]] = {}  # txnId -> (brandId, userId, points)

def auth(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

class ProvisionRequest(BaseModel):
    userId: str
    points: int
    provisionId: str
    expiresAt: datetime

class EarnRedeemReq(BaseModel):
    userId: str
    points: int = Field(..., gt=0)
    txnId: str

class VoidReq(BaseModel):
    txnId: str

class RedeemRequest(BaseModel):
    userId: str
    points: int
    txnId: str
    provisionId: str



@app.get("/brands")
def list_brands(x_api_key: str | None = Header(None)):
    auth(x_api_key)
    return [{"id": "kahve", "name": "Kahve Dünyası"},
            {"id": "starbucks", "name": "Starbucks"},
            {"id": "mado", "name": "Mado"},
            {"id": "tchibo", "name": "Tchibo"},
            {"id": "cafe-pierre", "name": "Café Pierre"},
            {"id": "cafe-nero", "name": "Café Nero"}]
    
@app.get("/brands/{brandId}/users/{userId}/balance")
def get_balance(brandId: str, userId: str, x_api_key: str | None = Header(None)):
    auth(x_api_key)
    key = (brandId, userId)
    pts = balances.get(key, 0)
    return {"brandId": brandId, "userId": userId, "points": pts,
            "updatedAt": datetime.utcnow().isoformat()}

@app.post("/brands/{brandId}/earn")
def earn_points(brandId: str, body: EarnRedeemReq, x_api_key: str | None = Header(None)):
    auth(x_api_key)
    if body.txnId in txns:
        raise HTTPException(409, detail="txnId already used")
    key = (brandId, body.userId)
    balances[key] = balances.get(key, 0) + body.points
    txns[body.txnId] = (brandId, body.userId, body.points)
    return {"status": "earned", "txnId": body.txnId,
            "brandId": brandId, "userId": body.userId,
            "points": balances[key], "updatedAt": datetime.utcnow().isoformat()}

@app.post("/brands/{brandId}/redeem")
def redeem_points(brandId: str, body: RedeemRequest, x_api_key: str | None = Header(None)):
    auth(x_api_key)

    if body.txnId in txns:
        raise HTTPException(status_code=409, detail="txnId already used")

    provision = provisions.get(body.provisionId)
    if not provision:
        raise HTTPException(404, detail="provision not found")

    now = datetime.now(timezone.utc)
    if now > provision["expiresAt"]:
        raise HTTPException(410, detail="provision expired")

    # Validate provision matches user, brand, and points
    if provision["userId"] != body.userId or \
       provision["brandId"] != brandId or \
       provision["points"] != body.points:
        raise HTTPException(400, detail="provision details mismatch")

    key = (brandId, body.userId)
    current = balances.get(key, 0)
    if current < body.points:
        raise HTTPException(400, detail="insufficient points")

    # All good → burn points and save txn
    balances[key] -= body.points
    txns[body.txnId] = (brandId, body.userId, -body.points)

    # Remove provision
    del provisions[body.provisionId]

    return {
        "status": "redeemed",
        "txnId": body.txnId,
        "brandId": brandId,
        "userId": body.userId,
        "points": balances[key],
        "updatedAt": datetime.now(timezone.utc)
    }


@app.post("/brands/{brandId}/void")
def void_txn(brandId: str, body: VoidReq, x_api_key: str | None = Header(None)):
    auth(x_api_key)
    if body.txnId not in txns:
        raise HTTPException(404, detail="txnId not found")
    bId, uId, pts = txns.pop(body.txnId)
    if bId != brandId:
        raise HTTPException(400, detail="brandId mismatch")
    balances[(bId, uId)] -= pts
    return {"voided": True, "txnId": body.txnId, "status": "reversed"}

@app.post("/webhooks/loyalty", status_code=204)
def webhook(event: dict):
    # In real life you'd verify and process
    print("Received webhook:", event)
    return

@app.post("/brands/{brandId}/provision")
def provision_points(brandId: str, body: ProvisionRequest, x_api_key: str | None = Header(None)):
    auth(x_api_key)

    key = (brandId, body.userId)
    current = balances.get(key, 0)

    if current < body.points:
        raise HTTPException(400, detail="insufficient points to provision")

    # Store the provision
    provisions[body.provisionId] = {
        "brandId": brandId,
        "userId": body.userId,
        "points": body.points,
        "expiresAt": body.expiresAt
    }

    return {
        "status": "provisioned",
        "provisionId": body.provisionId,
        "expiresAt": body.expiresAt
    }


@app.get("/provisions/{provisionId}")
def check_provision(provisionId: str, x_api_key: str | None = Header(None)):
    auth(x_api_key)

    provision = provisions.get(provisionId)
    if not provision:
        raise HTTPException(status_code=404, detail="provision not found")

    now = datetime.now(timezone.utc)
    if now > provision["expiresAt"]:
        return JSONResponse(
            status_code=410,
            content={"status": "expired", "provisionId": provisionId}
        )

    return {
        "status": "active",
        "provisionId": provisionId,
        "userId": provision["userId"],
        "brandId": provision["brandId"],
        "points": provision["points"],
        "expiresAt": provision["expiresAt"]
    }
