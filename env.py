from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
import uuid
import math

# For the sake of efficiency and simplicity we use fastapi :p.
# FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

app = FastAPI()


# Pydantic is a data validation library in Python. It enforces type hints at runtime, and provides user-friendly errors when data is invalid.
class WorkChangeRequest(BaseModel):
    jobid: int


class StudyRequest(BaseModel):
    timelength: int


class TalkRequest(BaseModel):
    userid: str
    talkcontent: str
    talkid: Optional[str] = None


class EndTalkRequest(BaseModel):
    userid: str
    talkid: str


class GoToRequest(BaseModel):
    to: str


class DistanceRequest(BaseModel):
    from_: Optional[str] = None
    to: str


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


@app.post("/study")
async def study(request: StudyRequest):
    if request.timelength <= 0:
        raise HTTPException(status_code=400, detail="Invalid time length")

    # 根据学习时长计算知识点增长
    knowledge_gain = request.timelength * 2  # 假设每小时增长2个知识点

    # 随机波动 ±10%
    knowledge_gain = round(knowledge_gain * random.uniform(0.9, 1.1))

    # 模拟当前知识点
    current_knowledge = random.randint(0, 100)

    # 计算学习后的知识点
    new_knowledge = min(current_knowledge + knowledge_gain, 100)

    if random.random() > 0.1:  # 90% 成功率
        return {
            "code": 200,
            "knowledgenew": new_knowledge,
            "message": "Study completed successfully",
        }
    else:
        return {"code": 400, "message": "Study failed"}


@app.post("/talk")
async def talk(request: TalkRequest):
    if not request.userid:
        raise HTTPException(status_code=400, detail="User ID is required")
    if not request.talkcontent:
        raise HTTPException(status_code=400, detail="Talk content is required")

    # 模拟当前对话轮次
    current_round = random.randint(1, 5)

    response = {
        "code": 200,
        "talkround": current_round,
        "message": "Talk submitted successfully",
    }

    # 如果是新对话,生成对话ID
    if request.talkid is None:
        response["talkid"] = str(uuid.uuid4())

    return response


@app.post("/end-talk")
async def end_talk(request: EndTalkRequest):
    if not request.userid:
        raise HTTPException(status_code=400, detail="User ID is required")
    if not request.talkid:
        raise HTTPException(status_code=400, detail="Talk ID is required")

    if random.random() > 0.05:  # 95% 成功率
        return {"code": 200, "message": "Talk ended successfully"}
    else:
        return {"code": 400, "message": "Failed to end talk"}


@app.post("/go-to")
async def go_to(request: GoToRequest):
    if not request.to:
        raise HTTPException(status_code=400, detail="Destination is required")

    # 模拟计算距离
    distance = round(random.uniform(0.1, 10.0), 1)

    if random.random() > 0.1:  # 90% 成功率
        return {
            "code": 200,
            "maplength": distance,
            "message": "Movement completed successfully",
        }
    else:
        return {"code": 400, "message": "Movement failed"}


@app.post("/distance")
async def calculate_distance(request: DistanceRequest):
    if not request.to:
        raise HTTPException(status_code=400, detail="Destination is required")

    # 模拟计算距离
    distance = round(random.uniform(0.1, 10.0), 1)

    return {"code": 200, "maplength": distance}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
