from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
#For the sake of efficiency and simplicity we use fastapi :p.
#FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

app = FastAPI()

#Pydantic is a data validation library in Python. It enforces type hints at runtime, and provides user-friendly errors when data is invalid.
class WorkChangeRequest(BaseModel):
    jobid: int

class ResumeSubmissionRequest(BaseModel):
    jobid: int
    cvurl: str

class VoteRequest(BaseModel):
    userid: str

class PublicJobRequest(BaseModel):
    jobid: int
    timelength: int

class FreelanceJobRequest(BaseModel):
    timelength: int
    merchantid: Optional[int] = None

# I will just add a simple endpoint to change the job of a character. -Rick
###
#将角色工作变更为非公共类的目标工作
###

@app.post("/work-change")
async def work_change(request: WorkChangeRequest):
    if request.jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    #We need to add stochasticity in the json.
    if random.random() > 0.5:
        return {"code": 200, "message": "Job change successful"}
    else:
        return {"code": 400, "message": "Job change failed"}

@app.post("/resume-submission")
async def resume_submission(request: ResumeSubmissionRequest):
    if request.jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    if not request.cvurl:
        raise HTTPException(status_code=400, detail="CV URL is required")
    #We need to add stochasticity in the json.
    if random.random() > 0.5:
        return {"code": 200, "message": "Resume submitted successfully"}
    else:
        return {"code": 400, "message": "Resume submission failed"}

@app.post("/vote")
async def vote(request: VoteRequest):
    if not request.userid:
        raise HTTPException(status_code=400, detail="User ID is required")
    # It seems that we do not need to add stochasticity in the json.
    return {"code": 200, "message": "Vote submitted successfully"}

@app.post("/public-job")
async def public_job(request: PublicJobRequest):
    if request.jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    if request.timelength <= 0:
        raise HTTPException(status_code=400, detail="Invalid time length")
    
    # 根据时长计算基础奖励
    base_reward = request.timelength * 10  # 假设每小时10金币
    
    # 随机波动 ±20%
    cashreward = base_reward * random.uniform(0.8, 1.2)
    
    if random.random() > 0.3:  # 70% 成功率
        return {
            "code": 200,
            "cashreward": round(cashreward, 2),
            "message": "Public job completed successfully"
        }
    else:
        return {
            "code": 400,
            "message": "Public job failed"
        }

@app.post("/freelance-job")
async def freelance_job(request: FreelanceJobRequest):
    if request.timelength <= 0:
        raise HTTPException(status_code=400, detail="Invalid time length")
    
    # 根据时长计算基础奖励
    base_reward = request.timelength * 15  # 假设每小时15金币
    
    # 随机波动 ±20%
    cashreward = base_reward * random.uniform(0.8, 1.2)
    
    response = {
        "code": 200,
        "cashreward": round(cashreward, 2),
        "message": "Freelance job completed successfully"
    }
    
    # 如果有商户ID，添加商品奖励和消耗
    if request.merchantid is not None:
        response.update({
            "merchantrewardid": random.randint(1, 10),
            "merchantrewardnum": random.randint(1, 5),
            "merchantspentid": random.randint(1, 10)
        })
    
    if random.random() > 0.2:  # 80% 成功率
        return response
    else:
        return {
            "code": 400,
            "message": "Freelance job failed"
        }

@app.get("/freelance-jobs")
async def get_freelance_jobs(jobid: Optional[int] = None):
    if jobid is not None and jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    return {"jobs": [{"jobid": 1, "jobname": "Apple Picker", "workhours": "10:00-16:00"}]}


@app.get("/freelance-jobs")
async def get_freelance_jobs(jobid: Optional[int] = None):
    # 在此处添加你的查询逻辑
    if jobid is not None and jobid < 0:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    # 模拟返回
    return {"jobs": [{"jobid": 1, "jobname": "Apple Picker", "workhours": "10:00-16:00"}]}

if __name__ == "__main__":
    #uvicorn is a lightning-fast ASGI server implementation, using uvloop and httptools.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)