from fastapi import FastAPI, HTTPException

from typing import Optional
import random

from model import WorkChangeRequest, TradeRequest, UseRequest, SleepRequest
from fake_data import (
    FreelanceJob,
    PublicJob,
    public_jobs_data,
    freelance_jobs_data,
    GameSubject,
    game_subjects_data,
)
from typing import List
from loguru import logger

# For the sake of efficiency and simplicity we use fastapi :p.
# FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

app = FastAPI()
logger.level("INFO")
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


# Get rick1-5


@app.get("/freelance-jobs", response_model=List[FreelanceJob])
async def get_freelance_jobs(jobid: Optional[int] = None):
    # 如果 jobid 为空，返回所有数据
    if jobid is None:
        return freelance_jobs_data

    # 如果 jobid 不为空，返回匹配的条目
    filtered_jobs = [job for job in freelance_jobs_data if job.jobid == jobid]

    if not filtered_jobs:
        raise HTTPException(status_code=404, detail="Job ID not found")

    return filtered_jobs


@app.get("/public-jobs", response_model=List[PublicJob])
async def get_public_jobs(jobid: Optional[int] = None):
    # 如果 jobid 为空，返回所有公共职业数据
    if jobid is None:
        return public_jobs_data

    # 如果 jobid 不为空，返回匹配的条目
    filtered_jobs = [job for job in public_jobs_data if job.jobid == jobid]

    if not filtered_jobs:
        raise HTTPException(status_code=404, detail="Job ID not found")

    return filtered_jobs


@app.get("/activity", response_model=List[GameSubject])
async def get_activity_subjects(subjectid: Optional[int] = None):
    # 如果 subjectid 为空，返回所有项目数据
    if subjectid is None:
        return game_subjects_data

    # 如果 subjectid 不为空，返回匹配的条目
    filtered_subjects = [
        subject for subject in game_subjects_data if subject.subjectid == subjectid
    ]
    logger.info(filtered_subjects)
    if not filtered_subjects:
        raise HTTPException(status_code=404, detail="Subject ID not found")

    return filtered_subjects


@app.get("/talk_data", response_model=dict)
async def get_talk(talkid: str):
    import datetime
    import pytz

    random_names = ["Elon", "CZ", "Alice", "Bob", "Charlie"]
    random_speakers = [random.choice(random_names) for _ in range(2)]

    # Generate random start time within the last 24 hours
    now = datetime.datetime.now(pytz.utc)
    random_start_time = now - datetime.timedelta(
        hours=random.randint(0, 23), minutes=random.randint(0, 59)
    )

    # Generate random end time between 15 to 45 minutes after start time
    random_end_time = random_start_time + datetime.timedelta(
        minutes=random.randint(15, 45)
    )

    # Format times as ISO 8601 strings
    random_start_time_str = random_start_time.isoformat()
    random_end_time_str = random_end_time.isoformat()

    # Generate random dummy data
    talk_data = {
        "talkid": talkid,
        "talkstarttime": random_start_time_str,
        "talkendtime": random_end_time_str,
        "istalkend": random.choice([True, False]),
        "talkdetails": [
            {
                "speaker": random_speakers[0],
                "message": "Hello, how are you?",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=5)
                ).isoformat(),
                "round": 1,
            },
            {
                "speaker": random_speakers[1],
                "message": "I'm good, thank you! How about you?",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=7)
                ).isoformat(),
                "round": 2,
            },
            {
                "speaker": random_speakers[0],
                "message": "I'm doing well. Have you heard about the new project?",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=10)
                ).isoformat(),
                "round": 3,
            },
            {
                "speaker": random_speakers[1],
                "message": "No, I haven't. Can you tell me more about it?",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=13)
                ).isoformat(),
                "round": 4,
            },
            {
                "speaker": random_speakers[0],
                "message": "Sure! It's a new AI-driven initiative that aims to revolutionize our industry.",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=16)
                ).isoformat(),
                "round": 5,
            },
            {
                "speaker": random_speakers[1],
                "message": "That sounds fascinating! I'd love to hear more details.",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=19)
                ).isoformat(),
                "round": 6,
            },
            {
                "speaker": random_speakers[0],
                "message": "Absolutely! Let's schedule a meeting to discuss it further.",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=22)
                ).isoformat(),
                "round": 7,
            },
            {
                "speaker": random_speakers[1],
                "message": "Great idea! I'll send you some available times later today.",
                "timestamp": (
                    random_start_time + datetime.timedelta(minutes=25)
                ).isoformat(),
                "round": 8,
            },
        ],
        "userid": random_speakers[0],
    }

    return talk_data


@app.get("/position")
async def get_position(
    coordinate: Optional[str] = None, positionid: Optional[str] = None
):
    # Mock data for positions
    class Coordinate:
        def __init__(self, latitude: float, longitude: float):
            self.latitude = latitude
            self.longitude = longitude

        def __str__(self):
            return f"{self.latitude},{self.longitude}"

        @classmethod
        def from_string(cls, coord_str: str):
            lat, lon = map(float, coord_str.split(","))
            return cls(lat, lon)

    positions = [
        {
            "positionid": "001",
            "positionname": "Bakery",
            "coordinate": Coordinate(40.7128, -74.0060),
        },
        {
            "positionid": "002",
            "positionname": "Wheat Mill",
            "coordinate": Coordinate(40.7829, -73.9654),
        },
        {
            "positionid": "003",
            "positionname": "Tool Workshop",
            "coordinate": Coordinate(40.7580, -73.9855),
        },
        {
            "positionid": "004",
            "positionname": "Smeltery",
            "coordinate": Coordinate(40.7589, -73.9851),
        },
        {
            "positionid": "005",
            "positionname": "School",
            "coordinate": Coordinate(40.7614, -73.9776),
        },
        {
            "positionid": "006",
            "positionname": "Hospital",
            "coordinate": Coordinate(40.7606, -73.9555),
        },
        {
            "positionid": "007",
            "positionname": "Town Hall",
            "coordinate": Coordinate(40.7127, -74.0059),
        },
        {
            "positionid": "008",
            "positionname": "Orchard",
            "coordinate": Coordinate(40.7829, -73.9654),
        },
        {
            "positionid": "009",
            "positionname": "Mining Area",
            "coordinate": Coordinate(40.7484, -73.9857),
        },
    ]

    if coordinate:
        # Search by coordinate
        for position in positions:
            if position["coordinate"] == coordinate:
                return position
        raise HTTPException(
            status_code=404, detail="Position not found for given coordinate"
        )

    elif positionid:
        # Search by positionid
        for position in positions:
            if position["positionid"] == positionid:
                return position
        raise HTTPException(
            status_code=404, detail="Position not found for given positionid"
        )

    else:
        return positions


if __name__ == "__main__":
    # uvicorn is a lightning-fast ASGI server implementation, using uvloop and httptools.
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
