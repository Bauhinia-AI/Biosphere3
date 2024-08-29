from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import random

# For the sake of efficiency and simplicity we use fastapi :p.
# FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

app = FastAPI()


# Pydantic is a data validation library in Python. It enforces type hints at runtime, and provides user-friendly errors when data is invalid.
class WorkChangeRequest(BaseModel):
    jobid: int


class TradeRequest(BaseModel):
    merchantid: int
    merchantnum: int
    transactiontype: int


class UseRequest(BaseModel):
    merchantid: int
    merchantnum: int


class SleepRequest(BaseModel):
    timelength: int


# item and effect data
item_dict = {
    "1": {
        "item_id": "potion_001",
        "name": "Strength Potion",
        "description": "A potion that temporarily increases strength.",
        "effects": [
            {
                "attribute": "strength",
                "modifier": 10,
                "duration": 600,
                "type": "temporary",
            },
            {
                "attribute": "health_regen",
                "modifier": 5,
                "duration": 300,
                "type": "temporary",
            },
        ],
        "side_effects": [
            {
                "attribute": "agility",
                "modifier": -2,
                "duration": 600,
                "type": "temporary",
            }
        ],
        "cooldown": 1200,
    },
    "2": {
        "item_id": "potion_002",
        "name": "Agility Elixir",
        "description": "An elixir that temporarily boosts agility.",
        "effects": [
            {
                "attribute": "agility",
                "modifier": 15,
                "duration": 600,
                "type": "temporary",
            },
            {
                "attribute": "dodge_chance",
                "modifier": 10,
                "duration": 300,
                "type": "temporary",
            },
        ],
        "side_effects": [
            {
                "attribute": "strength",
                "modifier": -3,
                "duration": 600,
                "type": "temporary",
            }
        ],
        "cooldown": 1500,
    },
    "3": {
        "item_id": "potion_003",
        "name": "Health Tonic",
        "description": "A tonic that greatly restores health over time.",
        "effects": [
            {
                "attribute": "health_regen",
                "modifier": 20,
                "duration": 300,
                "type": "temporary",
            }
        ],
        "side_effects": [
            {
                "attribute": "mana_regen",
                "modifier": -5,
                "duration": 300,
                "type": "temporary",
            }
        ],
        "cooldown": 900,
    },
}

# I will just add a simple endpoint to change the job of a character. -Rick
###
# 将角色工作变更为非公共类的目标工作
###


@app.post("/work-change")
async def work_change(request: WorkChangeRequest):
    if request.jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    # We need to add stochasticity in the json.
    if random.random() > 0.5:
        return {"code": 200, "message": "Job change successful"}
    else:
        return {"code": 400, "message": "Job change failed"}


@app.get("/freelance-jobs")
async def get_freelance_jobs(jobid: Optional[int] = None):
    # 在此处添加你的查询逻辑
    if jobid is not None and jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    # 模拟返回
    return {
        "jobs": [{"jobid": 1, "jobname": "Apple Picker", "workhours": "10:00-16:00"}]
    }


# 6-9 zesen
@app.post("/trade")
async def trade(request: TradeRequest):
    if request.merchantid < 0:
        raise HTTPException(status_code=400, detail="Invalid merchant ID")
    if request.merchantnum < 0:
        raise HTTPException(status_code=400, detail="Invalid merchant number")
    if request.transactiontype != 0 and request.transactiontype != 1:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
    # We need to add stochasticity in the json.
    if random.random() > 0.3:
        return {"code": 200}
    else:
        return {"code": 400}


@app.post("/use")
async def use(request: UseRequest):
    if not request.merchantnum:
        request.merchantnum = 1
    if request.merchantid < 0:
        raise HTTPException(status_code=400, detail="Invalid merchant ID")
    if request.merchantnum < 0:
        raise HTTPException(status_code=400, detail="Invalid merchant number")
    # We need to add stochasticity in the json.
    if random.random() > 0.3:
        return {"code": 200, "useeffect": item_dict[str(request.merchantid)]}
    else:
        return {"code": 400, "message": "Use failed"}


@app.post("/see-doctor")
async def see_doctor():
    # We need to add stochasticity in the json.
    if random.random() > 0.3:
        return {"code": 200, "healthnew": random.randint(50, 100)}
    else:
        return {"code": 400, "message": "You are sick."}


@app.post("/sleep")
async def sleep(request: SleepRequest):
    if request.timelength < 0:
        raise HTTPException(status_code=400, detail="Invalid time length")
    if request.timelength > 10:
        raise HTTPException(
            status_code=400, detail="You cannot sleep for more than 10 hours."
        )
    # We need to add stochasticity in the json.
    if random.random() > 0.3:
        return {"code": 200, "energynew": 10 * request.timelength}
    else:
        return {"code": 400, "message": "You cannot sleep."}


if __name__ == "__main__":
    # uvicorn is a lightning-fast ASGI server implementation, using uvloop and httptools.
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
