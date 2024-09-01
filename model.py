from pydantic import BaseModel
from typing import Dict, Optional

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


class FreelanceJob(BaseModel):
    jobname: str
    jobid: int
    workhours: str
    wageperhour: float
    wagemerchant: str
    wagemerchantperhour: int
    merchantspend: str
    merchantspendperhour: int
    cashspend: int

class PublicJob(BaseModel):
    jobname: str
    jobid: int
    workhours: str
    wageperhour: float
    cvday: str
    voteday: str
    jobamount: Optional[int]
    jobavailable: Optional[int]

class GameSubject(BaseModel):
    subjectname: str
    subjectid: int
    availablehours: str
    requirements: Dict[str, int]  # 键为属性名，值为所需数值
    spendings: Dict[str, int]     # 键为消耗类型，值为消耗数值
    rewards: Dict[str, int]       # 键为奖励类型，值为奖励数值