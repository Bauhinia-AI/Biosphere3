from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
#For the sake of efficiency and simplicity we use fastapi :p.
#FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

app = FastAPI()

#Pydantic is a data validation library in Python. It enforces type hints at runtime, and provides user-friendly errors when data is invalid.
class WorkChangeRequest(BaseModel):
    jobid: int

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