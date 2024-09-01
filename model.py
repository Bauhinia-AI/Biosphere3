from pydantic import BaseModel
from typing import Dict, Optional, List


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
    spendings: Dict[str, int]  # 键为消耗类型，值为消耗数值
    rewards: Dict[str, int]  # 键为奖励类型，值为奖励数值


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


class ResumeSubmissionRequest(BaseModel):
    jobid: int
    cvurl: str


class WorkChangeRequest(BaseModel):
    jobid: str


class VoteRequest(BaseModel):
    userid: str


class PublicJobRequest(BaseModel):
    jobid: int
    timelength: int


class FreelanceJobRequest(BaseModel):
    timelength: int
    merchantid: Optional[int] = None


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
