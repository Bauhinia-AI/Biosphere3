# app/api.py
import logging
from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from pyparsing import Union
import uvicorn
import sys
import os
import time
from enum import Enum
from pymongo.errors import PyMongoError, DuplicateKeyError

# Ensure the parent directory is in the Python path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_utils import MongoDBUtils
from database.domain_specific_queries import DomainSpecificQueries
from fastapi.middleware.cors import CORSMiddleware

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_directory = os.path.join(project_root, "logs")
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "api.log")),
        logging.StreamHandler(),
    ],
)

app = FastAPI()

# 配置允许跨域的源
origins = [
    "https://bio3-roan.vercel.app",  # 允许的源，可以添加多个
    "*",  # 如果需要允许所有来源
]

# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的 HTTP 头部
)


class StandardResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


def success_response(data: Any, message: str = "Operation successful.") -> Dict:
    return {"code": 1, "message": message, "data": data}


def failure_response(message: str, data: Any = None) -> Dict:
    return {"code": 0, "message": message, "data": data}


try:
    db_utils = MongoDBUtils()
    domain_queries = DomainSpecificQueries(db_utils=db_utils)
    logging.info("Successfully initialized database utilities.")
except Exception as e:
    logging.critical(f"Failed to initialize database utilities: {e}")
    sys.exit(1)


@app.exception_handler(PyMongoError)
async def pymongo_exception_handler(request: Request, exc: PyMongoError):
    logging.error(f"PyMongoError: {exc}")
    return JSONResponse(
        status_code=200, content=failure_response(message="Database error.")
    )


@app.exception_handler(DuplicateKeyError)
async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    logging.error(f"DuplicateKeyError: {exc}")
    return JSONResponse(
        status_code=200,
        content=failure_response(message=f"Duplicate entry error: {str(exc)}"),
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logging.error(f"HTTPException: {exc.detail}")
    status_messages = {
        400: "Bad request. The server could not understand the request due to invalid syntax.",
        401: "Unauthorized access. Authentication is required and has failed or has not been provided.",
        403: "Forbidden. You do not have permission to access this resource.",
        404: "Resource not found. The requested resource could not be found on the server.",
        405: "Method not allowed.",
        409: "Conflict error.",
        410: "Gone.",
        413: "Payload too large.",
        415: "Unsupported media type.",
        422: "Unprocessable entity.",
        429: "Too many requests.",
        500: "Internal server error.",
        501: "Not implemented.",
        502: "Bad gateway.",
        503: "Service unavailable.",
        504: "Gateway timeout.",
        307: "Temporary redirect.",
    }

    message = status_messages.get(
        exc.status_code,
        "An error occurred. Please refer to the specific error code for more details.",
    )
    return JSONResponse(status_code=200, content=failure_response(message=message))


from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_details = []
    for error in errors:
        loc = " -> ".join([str(loc) for loc in error["loc"]])
        msg = error["msg"]
        error_details.append(f"{loc}: {msg}")
    error_message = "Validation error. " + "; ".join(error_details)
    logging.error(f"RequestValidationError: {error_message}")
    return JSONResponse(
        status_code=200, content=failure_response(message=error_message)
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=200,
        content=failure_response(message=f"Unhandled exception: {exc}"),
    )


from typing import Optional, List, Dict
from pydantic import BaseModel


class InsertRequest(BaseModel):
    collection_name: str
    document: dict


class UpdateRequest(BaseModel):
    collection_name: str
    query: dict
    update: dict
    upsert: Optional[bool] = False
    multi: Optional[bool] = False


class DeleteRequest(BaseModel):
    collection_name: str
    query: dict
    multi: Optional[bool] = False


class FindRequest(BaseModel):
    collection_name: str
    query: Optional[dict] = {}
    projection: Optional[dict] = None
    limit: Optional[int] = 0
    sort: Optional[List] = None


class VectorSearchRequest(BaseModel):
    query_text: str
    fields_to_return: List[str]
    collection_name: str
    k: Optional[int] = 1


class LatestKDocumentsRequest(BaseModel):
    collection_name: str
    characterId: int
    k: Optional[int] = 1
    item: str


class EncounterCountRequest(BaseModel):
    from_id: int
    to_id: int


class StoreEncounterCountRequest(BaseModel):
    from_id: int
    to_id: int
    count: Optional[int] = 1


class GetEncountersByFromIdRequest(BaseModel):
    from_id: int
    k: Optional[int] = 1


class UpdateEncounterCountRequest(BaseModel):
    from_id: int
    to_id: int
    count: int


class IntimacyRequest(BaseModel):
    from_id: Optional[int] = None
    to_id: Optional[int] = None
    intimacy_level_min: Optional[int] = None
    intimacy_level_max: Optional[int] = None
    have_conversation: Optional[bool] = False


class StoreIntimacyRequest(BaseModel):
    from_id: int
    to_id: int
    intimacy_level: Optional[int] = 50


class UpdateIntimacyRequest(BaseModel):
    from_id: int
    to_id: int
    new_intimacy_level: int


class ImpressionRequest(BaseModel):
    from_id: int
    to_id: int
    k: Optional[int] = 1


class StoreImpressionRequest(BaseModel):
    from_id: int
    to_id: int
    impression: str


class StoreCVRequest(BaseModel):
    jobid: int
    characterId: int
    CV_content: str
    week: int
    health: int  # 新增字段
    studyxp: int  # 新增字段
    date: int  # 新增字段
    jobName: str  # 新增字段
    election_status: Optional[str] = "not_yet"  # 更新字段名


class UpdateElectionResultRequest(BaseModel):
    characterId: int
    election_status: str
    jobid: Optional[int] = None
    week: Optional[int] = None


class GetCVRequest(BaseModel):
    jobid: Optional[int] = None
    characterId: Optional[int] = None
    week: Optional[int] = None
    election_status: Optional[str] = None


class StoreDescriptorRequest(BaseModel):
    failed_action: str
    action_id: int
    characterId: int
    reflection: str


class GetDescriptorRequest(BaseModel):
    action_id: int
    characterId: int
    k: Optional[int] = 1


class StoreDailyObjectiveRequest(BaseModel):
    characterId: int
    objectives: List[str]


class GetDailyObjectivesRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class StorePlanRequest(BaseModel):
    characterId: int
    detailed_plan: str


class GetPlansRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class StoreMetaSeqRequest(BaseModel):
    characterId: int
    meta_sequence: List[str]


class GetMetaSequencesRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class UpdateMetaSeqRequest(BaseModel):
    characterId: int
    meta_sequence: List[str]


class StoreKnowledgeRequest(BaseModel):
    characterId: int
    day: int
    environment_information: str
    personal_information: str


class GetKnowledgeRequest(BaseModel):
    characterId: int
    day: int


class GetLatestKnowledgeRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class UpdateKnowledgeRequest(BaseModel):
    characterId: int
    day: int
    environment_information: Optional[str] = None
    personal_information: Optional[str] = None


class StoreDiaryRequest(BaseModel):
    characterId: int
    diary_content: str


class GetDiariesRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class StorecharacterRequest(BaseModel):
    characterId: int
    characterName: Optional[str] = None
    gender: Optional[str] = None
    spriteId: Optional[int] = 0
    relationship: Optional[str] = None
    personality: Optional[str] = None
    long_term_goal: Optional[str] = None
    short_term_goal: Optional[str] = None
    language_style: Optional[str] = None
    biography: Optional[str] = None


class characterRAGRequest(BaseModel):
    characterId: int
    topic: str
    k: Optional[int] = 1


class GetcharacterRequest(BaseModel):
    characterId: Optional[int] = None


class CharacterRAGInListRequest(BaseModel):
    characterId: int
    characterList: List[int]
    topic: str
    k: Optional[int] = 1


class UpdatecharacterRequest(BaseModel):
    characterId: int
    update_fields: dict


class SampleItem(str, Enum):
    relationship = "relationship"
    personality = "personality"
    long_term_goal = "long_term_goal"
    short_term_goal = "short_term_goal"
    language_style = "language_style"
    biography = "biography"


class SampleRequest(BaseModel):
    item_name: Optional[SampleItem] = None


class AgentPromptRequest(BaseModel):
    characterId: int
    daily_goal: Optional[str] = None
    refer_to_previous: Optional[bool] = None
    life_style: Optional[str] = None
    daily_objective_ar: Optional[str] = None
    task_priority: Optional[list] = None
    max_actions: Optional[int] = None
    meta_seq_ar: Optional[str] = None
    replan_time_limit: Optional[int] = None
    meta_seq_adjuster_ar: Optional[str] = None
    focus_topic: Optional[list] = None
    depth_of_reflection: Optional[str] = None
    reflection_ar: Optional[str] = None
    level_of_detail: Optional[str] = None
    tone_and_style: Optional[str] = None


class UpdateAgentPromptRequest(BaseModel):
    characterId: int
    update_fields: dict


class GetAgentPromptRequest(BaseModel):
    characterId: int


class DeleteAgentPromptRequest(BaseModel):
    characterId: int


class StoreConversationPromptRequest(BaseModel):
    characterId: int
    topic_requirements: Optional[str] = None
    relation: Optional[str] = None
    emotion: Optional[str] = None
    personality: Optional[str] = None
    habits_and_preferences: Optional[str] = None


class UpdateConversationPromptRequest(BaseModel):
    characterId: int
    update_fields: Dict[str, Optional[str]]


class GetConversationPromptRequest(BaseModel):
    characterId: int


class DeleteConversationPromptRequest(BaseModel):
    characterId: int


class StoreDecisionRequest(BaseModel):
    characterId: int
    need_replan: Optional[bool] = None
    action_description: Optional[List[str]] = None
    action_result: Optional[List[str]] = None
    new_plan: Optional[List[str]] = None
    daily_objective: Optional[List[str]] = None
    meta_seq: Optional[List[str]] = None
    reflection: Optional[List[str]] = None


class GetDecisionRequest(BaseModel):
    characterId: int
    count: Optional[int] = None


class CurrentPointerRequest(BaseModel):
    characterId: int
    current_pointer: str


class StoreConversationRequest(BaseModel):
    from_id: int
    to_id: int
    start_time: str
    start_day: int
    message: str
    send_gametime: List[Union[int, str]]
    send_realtime: str


class GetConversationByListRequest(BaseModel):
    characterIds: List[int]
    time: Optional[str] = None
    k: Optional[int] = None


class StoreConversationMemoryRequest(BaseModel):
    characterId: int
    day: int
    topic_plan: Optional[List[str]] = None
    time_list: Optional[List[str]] = None
    started: Optional[List[dict]] = None


class UpdateConversationMemoryRequest(BaseModel):
    characterId: int
    day: int
    update_fields: Optional[dict] = None
    add_started: Optional[dict] = None


class StoreWorkExperienceRequest(BaseModel):
    characterId: int
    jobid: int
    start_date: int


class UpdateWorkExperienceRequest(BaseModel):
    characterId: int
    jobid: int
    additional_work: int
    additional_salary: float


class StoreCharacterArcRequest(BaseModel):
    characterId: int
    belief: Optional[str] = None
    mood: Optional[str] = None
    values: Optional[str] = None
    habits: Optional[str] = None
    personality: Optional[str] = None


class StoreActionRequest(BaseModel):
    characterId: str
    actionName: str
    gameTime: str


def retry_operation(func, retries=3, delay=2, *args, **kwargs):
    # for attempt in range(1, retries + 1):
    #     try:
    #         return func(*args, **kwargs)
    #     except DuplicateKeyError as e:
    #         logging.info(f"Duplicate key error: {e}")
    #         raise e
    #     except PyMongoError as e:
    #         logging.error(f"PyMongoError on attempt {attempt}: {e}")
    #         if attempt < retries:
    #             logging.info(f"Retrying in {delay} seconds...")
    #             time.sleep(delay)
    #         else:
    #             logging.critical(f"Operation failed after {retries} attempts.")
    #             raise e
    #     except Exception as e:
    #         logging.error(f"Unexpected error on attempt {attempt}: {e}")
    #         if attempt < retries:
    #             logging.info(f"Retrying in {delay} seconds...")
    #             time.sleep(delay)
    #         else:
    #             logging.critical(
    #                 f"Operation failed after {retries} attempts due to unexpected error."
    #             )
    #             raise e
    return func(*args, **kwargs)


crud_router = APIRouter(prefix="/crud", tags=["CRUD Operations"])


@crud_router.post("/insert", response_model=StandardResponse)
def insert_data(request: InsertRequest):
    inserted_id = retry_operation(
        db_utils.insert_document,
        retries=3,
        delay=2,
        collection_name=request.collection_name,
        document=request.document,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Document inserted successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to insert document.")


@crud_router.put("/update", response_model=StandardResponse)
def update_data(request: UpdateRequest):
    modified_count = retry_operation(
        db_utils.update_documents,
        retries=3,
        delay=2,
        collection_name=request.collection_name,
        query=request.query,
        update=request.update,
        upsert=request.upsert,
        multi=request.multi,
    )
    if modified_count is not None:
        return success_response(
            data=modified_count, message="Documents updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No documents were updated.")


@crud_router.delete("/delete", response_model=StandardResponse)
def delete_data(request: DeleteRequest):
    if request.multi:
        deleted_count = retry_operation(
            db_utils.delete_documents,
            retries=3,
            delay=2,
            collection_name=request.collection_name,
            query=request.query,
        )
        message = (
            "Multiple documents deleted successfully."
            if deleted_count
            else "No documents were deleted."
        )
    else:
        deleted_count = retry_operation(
            db_utils.delete_document,
            retries=3,
            delay=2,
            collection_name=request.collection_name,
            query=request.query,
        )
        message = (
            "Document deleted successfully."
            if deleted_count
            else "No document was deleted."
        )
    return success_response(data=deleted_count, message=message)


@crud_router.get("/find", response_model=StandardResponse)
def find_data(
    collection_name: str,
    query: Optional[str] = None,
    projection: Optional[str] = None,
    limit: Optional[int] = 0,
    sort: Optional[str] = None,
):
    # 这里需要将query、projection、sort从字符串转为实际的dict或list
    # 此处省略转换的实现细节
    documents = retry_operation(
        db_utils.find_documents,
        retries=3,
        delay=2,
        collection_name=collection_name,
        query={},  # 根据实际需要解析query字符串
        projection=None,
        limit=limit,
        sort=None,
    )
    if documents:
        return success_response(
            data=documents, message="Documents retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No documents found.")


vector_search_router = APIRouter(prefix="/vector_search", tags=["Vector Search"])


@vector_search_router.get("/", response_model=StandardResponse)
def vector_search_api(
    collection_name: str, query_text: str, fields_to_return: str, k: int = 1
):
    fields_list = fields_to_return.split(",")
    results = retry_operation(
        domain_queries.vector_search,
        retries=3,
        delay=2,
        collection_name=collection_name,
        query_text=query_text,
        fields_to_return=fields_list,
        k=k,
    )
    if results:
        return success_response(
            data=results, message="Vector search completed successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No results found for the vector search."
        )


impressions_router = APIRouter(prefix="/impressions", tags=["Impressions"])


@impressions_router.get("/", response_model=StandardResponse)
def get_impression_api(from_id: int, to_id: int, k: int = 1):
    impressions = retry_operation(
        domain_queries.get_impression_from_mongo,
        retries=3,
        delay=2,
        from_id=from_id,
        to_id=to_id,
        k=k,
    )
    if impressions:
        return success_response(
            data=impressions, message="Impressions retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No impressions found.")


@impressions_router.post("/", response_model=StandardResponse)
def store_impression_api(request: StoreImpressionRequest):
    inserted_id = retry_operation(
        domain_queries.store_impression,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
        impression=request.impression,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Impression stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store impression.")


intimacy_router = APIRouter(prefix="/intimacy", tags=["Intimacy"])


@intimacy_router.get("/", response_model=StandardResponse)
def get_intimacy_api(
    from_id: Optional[int] = None,
    to_id: Optional[int] = None,
    intimacy_level_min: Optional[int] = None,
    intimacy_level_max: Optional[int] = None,
    have_conversation: bool = False,
):
    intimacy = retry_operation(
        domain_queries.get_intimacy,
        retries=3,
        delay=2,
        from_id=from_id,
        to_id=to_id,
        intimacy_level_min=intimacy_level_min,
        intimacy_level_max=intimacy_level_max,
        have_conversation=have_conversation,
    )
    if intimacy:
        return success_response(
            data=intimacy, message="Intimacy level retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No intimacy level found.")


@intimacy_router.post("/", response_model=StandardResponse)
def store_intimacy_api(request: StoreIntimacyRequest):
    inserted_id = retry_operation(
        domain_queries.store_intimacy,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
        intimacy_level=request.intimacy_level,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Intimacy level stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store intimacy level.")


@intimacy_router.put("/", response_model=StandardResponse)
def update_intimacy_api(request: UpdateIntimacyRequest):
    current_intimacy = retry_operation(
        domain_queries.get_intimacy,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
    )

    if current_intimacy:
        result = retry_operation(
            domain_queries.update_intimacy,
            retries=3,
            delay=2,
            from_id=request.from_id,
            to_id=request.to_id,
            new_intimacy_level=request.new_intimacy_level,
        )
        if result:
            return success_response(
                data=result,
                message="Intimacy level updated successfully.",
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to update intimacy level."
            )
    else:
        raise HTTPException(
            status_code=404, detail="No intimacy level found to update."
        )


@intimacy_router.patch("/decrease_all", response_model=StandardResponse)
def decrease_all_intimacy_levels_api():
    result = retry_operation(
        domain_queries.decrease_all_intimacy_levels,
        retries=3,
        delay=2,
    )
    if result:
        return success_response(
            data=result,
            message="All intimacy levels decreased by 1 successfully.",
        )
    else:
        raise HTTPException(
            status_code=500, detail="Failed to decrease intimacy levels."
        )


encounter_count_router = APIRouter(prefix="/encounter_count", tags=["Encounter Count"])


@encounter_count_router.get("/", response_model=StandardResponse)
def get_encounter_count_api(from_id: int, to_id: int):
    encounter_count = retry_operation(
        domain_queries.get_encounter_count,
        retries=3,
        delay=2,
        from_id=from_id,
        to_id=to_id,
    )
    if encounter_count:
        return success_response(
            data=encounter_count, message="Encounter count retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No encounter count found.")


@encounter_count_router.get("/by_from_id", response_model=StandardResponse)
def get_encounter_count_by_from_id_api(from_id: int, k: int = 1):
    encounters = retry_operation(
        domain_queries.get_encounters_by_from_id,
        retries=3,
        delay=2,
        from_id=from_id,
        k=k,
    )
    if encounters:
        return success_response(
            data=encounters, message="Encounters retrieved successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No encounters found for the specified from_id."
        )


@encounter_count_router.post("/", response_model=StandardResponse)
def store_encounter_count_api(request: StoreEncounterCountRequest):
    inserted_id = retry_operation(
        domain_queries.store_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
        count=request.count,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Encounter count stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store encounter count.")


@encounter_count_router.put("/increment", response_model=StandardResponse)
def increment_encounter_count_api(request: EncounterCountRequest):
    current_count = retry_operation(
        domain_queries.get_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
    )
    if current_count:
        new_count = current_count[0]["count"] + 1
        result = retry_operation(
            domain_queries.update_encounter_count,
            retries=3,
            delay=2,
            from_id=request.from_id,
            to_id=request.to_id,
            new_count=new_count,
        )
        if result:
            return success_response(
                data=result, message="Encounter count incremented successfully."
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to increment encounter count."
            )
    else:
        inserted_id = retry_operation(
            domain_queries.store_encounter_count,
            retries=3,
            delay=2,
            from_id=request.from_id,
            to_id=request.to_id,
            count=1,
        )
        if inserted_id:
            return success_response(
                data=str(inserted_id), message="Encounter count created and set to 1."
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create encounter count."
            )


@encounter_count_router.put("/", response_model=StandardResponse)
def update_encounter_count_api(request: UpdateEncounterCountRequest):
    result = retry_operation(
        domain_queries.update_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
        new_count=request.count,
    )
    if result:
        return success_response(
            data=result, message="Encounter count updated successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to update encounter count.")


cvs_router = APIRouter(prefix="/cv", tags=["CVs"])


@cvs_router.post("/", response_model=StandardResponse)
def store_cv_api(request: StoreCVRequest):
    inserted_id = retry_operation(
        domain_queries.store_cv,
        retries=3,
        delay=2,
        jobid=request.jobid,
        characterId=request.characterId,
        CV_content=request.CV_content,
        week=request.week,
        health=request.health,
        studyxp=request.studyxp,
        date=request.date,
        jobName=request.jobName,
        election_status=request.election_status,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="CV stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store CV.")


@cvs_router.put("/election_status", response_model=StandardResponse)
def update_election_status_api(request: UpdateElectionResultRequest):
    result = retry_operation(
        domain_queries.update_election_status,
        retries=3,
        delay=2,
        characterId=request.characterId,
        election_status=request.election_status,
        jobid=request.jobid,
        week=request.week,
    )
    if result:
        return success_response(
            data=result, message="Election result updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No CV found to update.")


@cvs_router.get("/", response_model=StandardResponse)
def get_cv_api(
    jobid: Optional[int] = None,
    characterId: Optional[int] = None,
    week: Optional[int] = None,
    election_status: Optional[str] = None,
):
    cvs = retry_operation(
        domain_queries.get_cv,
        retries=3,
        delay=2,
        jobid=jobid,
        characterId=characterId,
        week=week,
        election_status=election_status,
    )
    if cvs:
        return success_response(data=cvs, message="CVs retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No CVs found.")


actions_router = APIRouter(prefix="/actions", tags=["Actions"])


@actions_router.post("/", response_model=StandardResponse)
def store_action_api(request: StoreActionRequest):
    inserted_id = retry_operation(
        domain_queries.store_action,
        retries=3,
        delay=2,
        characterId=request.characterId,
        actionName=request.actionName,
        gameTime=request.gameTime,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Action stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store action.")


@actions_router.get("/counts", response_model=StandardResponse)
def get_action_counts_api(from_time: str, to_time: str):
    action_counts = retry_operation(
        domain_queries.get_action_counts_in_time_range,
        retries=3,
        delay=2,
        from_time=from_time,
        to_time=to_time,
    )
    if action_counts:
        return success_response(
            data=action_counts, message="Action counts retrieved successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No actions found in the specified time range."
        )


descriptors_router = APIRouter(prefix="/descriptors", tags=["Descriptors"])


@descriptors_router.post("/", response_model=StandardResponse)
def store_descriptor_api(request: StoreDescriptorRequest):
    inserted_id = retry_operation(
        domain_queries.store_descriptor,
        retries=3,
        delay=2,
        failed_action=request.failed_action,
        action_id=request.action_id,
        characterId=request.characterId,
        reflection=request.reflection,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Descriptor stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store descriptor.")


@descriptors_router.get("/", response_model=StandardResponse)
def get_descriptor_api(action_id: int, characterId: int, k: int = 1):
    descriptors = retry_operation(
        domain_queries.get_descriptor,
        retries=3,
        delay=2,
        action_id=action_id,
        characterId=characterId,
        k=k,
    )
    if descriptors:
        return success_response(
            data=descriptors, message="Descriptors retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No descriptors found.")


daily_objectives_router = APIRouter(
    prefix="/daily_objectives", tags=["Daily Objectives"]
)


@daily_objectives_router.post("/", response_model=StandardResponse)
def store_daily_objective_api(request: StoreDailyObjectiveRequest):
    inserted_id = retry_operation(
        domain_queries.store_daily_objective,
        retries=3,
        delay=2,
        characterId=request.characterId,
        objectives=request.objectives,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Daily objectives stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store daily objectives.")


@daily_objectives_router.get("/", response_model=StandardResponse)
def get_daily_objectives_api(characterId: int, k: int = 1):
    objectives = retry_operation(
        domain_queries.get_daily_objectives,
        retries=3,
        delay=2,
        characterId=characterId,
        k=k,
    )
    if objectives:
        return success_response(
            data=objectives, message="Daily objectives retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No daily objectives found.")


plans_router = APIRouter(prefix="/plans", tags=["Plans"])


@plans_router.post("/", response_model=StandardResponse)
def store_plan_api(request: StorePlanRequest):
    inserted_id = retry_operation(
        domain_queries.store_plan,
        retries=3,
        delay=2,
        characterId=request.characterId,
        detailed_plan=request.detailed_plan,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Plan stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store plan.")


@plans_router.get("/", response_model=StandardResponse)
def get_plans_api(characterId: int, k: int = 1):
    plans = retry_operation(
        domain_queries.get_plans,
        retries=3,
        delay=2,
        characterId=characterId,
        k=k,
    )
    if plans:
        return success_response(data=plans, message="Plans retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No plans found.")


meta_sequences_router = APIRouter(prefix="/meta_sequences", tags=["Meta Sequences"])


@meta_sequences_router.post("/", response_model=StandardResponse)
def store_meta_seq_api(request: StoreMetaSeqRequest):
    inserted_id = retry_operation(
        domain_queries.store_meta_seq,
        retries=3,
        delay=2,
        characterId=request.characterId,
        meta_sequence=request.meta_sequence,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Meta sequence stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store meta sequence.")


@meta_sequences_router.get("/", response_model=StandardResponse)
def get_meta_sequences_api(characterId: int, k: int = 1):
    meta_sequences = retry_operation(
        domain_queries.get_meta_sequences,
        retries=3,
        delay=2,
        characterId=characterId,
        k=k,
    )
    if meta_sequences:
        return success_response(
            data=meta_sequences, message="Meta sequences retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No meta sequences found.")


@meta_sequences_router.put("/", response_model=StandardResponse)
def update_meta_seq_api(request: UpdateMetaSeqRequest):
    modified_count = retry_operation(
        domain_queries.update_meta_seq,
        retries=3,
        delay=2,
        characterId=request.characterId,
        meta_sequence=request.meta_sequence,
    )
    if modified_count is not None:
        return success_response(
            data=modified_count, message="Meta sequence updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No meta sequences were updated.")


knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@knowledge_router.post("/", response_model=StandardResponse)
def store_knowledge_api(request: StoreKnowledgeRequest):
    inserted_id = retry_operation(
        domain_queries.store_knowledge,
        retries=3,
        delay=2,
        characterId=request.characterId,
        day=request.day,
        environment_information=request.environment_information,
        personal_information=request.personal_information,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Knowledge stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store knowledge.")


@knowledge_router.get("/", response_model=StandardResponse)
def get_knowledge_api(characterId: int, day: int):
    knowledge = retry_operation(
        domain_queries.get_knowledge,
        retries=3,
        delay=2,
        characterId=characterId,
        day=day,
    )
    if knowledge:
        return success_response(
            data=knowledge, message="Knowledge retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No knowledge found.")


@knowledge_router.get("/latest", response_model=StandardResponse)
def get_latest_knowledge_api(characterId: int, k: int = 1):
    knowledge = retry_operation(
        domain_queries.get_latest_knowledge,
        retries=3,
        delay=2,
        characterId=characterId,
        k=k,
    )
    if knowledge:
        return success_response(
            data=knowledge, message="Latest knowledge retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No latest knowledge found.")


@knowledge_router.put("/", response_model=StandardResponse)
def update_knowledge_api(request: UpdateKnowledgeRequest):
    result = retry_operation(
        domain_queries.update_knowledge,
        retries=3,
        delay=2,
        characterId=request.characterId,
        day=request.day,
        environment_information=request.environment_information,
        personal_information=request.personal_information,
    )
    if result:
        return success_response(data=result, message="Knowledge updated successfully.")
    else:
        raise HTTPException(status_code=404, detail="No knowledge was updated.")


diaries_router = APIRouter(prefix="/diaries", tags=["Diaries"])


@diaries_router.post("/", response_model=StandardResponse)
def store_diary_api(request: StoreDiaryRequest):
    inserted_id = retry_operation(
        domain_queries.store_diary,
        retries=3,
        delay=2,
        characterId=request.characterId,
        diary_content=request.diary_content,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Diary entry stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store diary entry.")


@diaries_router.get("/", response_model=StandardResponse)
def get_diaries_api(characterId: int, k: int = 1):
    diaries = retry_operation(
        domain_queries.get_diaries,
        retries=3,
        delay=2,
        characterId=characterId,
        k=k,
    )
    if diaries:
        return success_response(data=diaries, message="Diaries retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No diaries found.")


characters_router = APIRouter(prefix="/characters", tags=["Characters"])


@characters_router.post("/", response_model=StandardResponse)
def store_character_api(request: StorecharacterRequest):
    existing_character = retry_operation(
        domain_queries.get_character,
        retries=3,
        delay=2,
        characterId=request.characterId,
    )

    if existing_character:
        return JSONResponse(
            status_code=200,
            content={
                "code": 2,
                "message": f"Character with characterId {request.characterId} already exists.",
                "data": None,
            },
        )

    sample_methods = {
        "relationship": lambda: domain_queries.get_relationship_sample()[0],
        "personality": lambda: ", ".join(domain_queries.get_personality_sample()),
        "long_term_goal": lambda: ", ".join(domain_queries.get_long_term_goal_sample()),
        "short_term_goal": lambda: ", ".join(
            domain_queries.get_short_term_goal_sample()
        ),
        "language_style": lambda: ", ".join(domain_queries.get_language_style_sample()),
        "biography": domain_queries.get_biography_sample,
    }

    character_data = {
        "characterId": request.characterId,
        "characterName": request.characterName,
        "gender": request.gender,
        "spriteId": request.spriteId,
        "relationship": request.relationship or sample_methods["relationship"](),
        "personality": request.personality or sample_methods["personality"](),
        "long_term_goal": request.long_term_goal or sample_methods["long_term_goal"](),
        "short_term_goal": request.short_term_goal
        or sample_methods["short_term_goal"](),
        "language_style": request.language_style or sample_methods["language_style"](),
        "biography": request.biography or sample_methods["biography"](),
    }

    inserted_id = retry_operation(
        domain_queries.store_character, retries=3, delay=2, **character_data
    )

    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Character stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store character.")


@characters_router.get("/", response_model=StandardResponse)
def get_character_api(characterId: Optional[int] = None):
    characters = retry_operation(
        domain_queries.get_character,
        retries=3,
        delay=2,
        characterId=characterId,
    )
    if characters:
        return success_response(
            data=characters, message="Characters retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No characters found.")


@characters_router.get("/rag", response_model=StandardResponse)
def get_character_rag_api(characterId: int, topic: str, k: int = 1):
    character_rag_results = retry_operation(
        domain_queries.get_character_RAG,
        retries=3,
        delay=2,
        characterId=characterId,
        topic=topic,
        k=k,
    )
    if character_rag_results:
        return success_response(
            data=character_rag_results,
            message="Character RAG results retrieved successfully.",
        )
    else:
        raise HTTPException(status_code=404, detail="No character RAG results found.")


@characters_router.post("/rag_in_list", response_model=StandardResponse)
def get_character_rag_in_list_api(request: CharacterRAGInListRequest):
    character_rag_results = retry_operation(
        domain_queries.get_character_RAG_in_list,
        retries=3,
        delay=2,
        characterId=request.characterId,
        characterList=request.characterList,
        topic=request.topic,
        k=request.k,
    )
    if character_rag_results:
        return success_response(
            data=character_rag_results,
            message="Character RAG in list results retrieved successfully.",
        )
    else:
        raise HTTPException(
            status_code=404, detail="No character RAG in list results found."
        )


@characters_router.put("/", response_model=StandardResponse)
def update_character_api(request: UpdatecharacterRequest):
    modified_count = retry_operation(
        domain_queries.update_character,
        retries=3,
        delay=2,
        characterId=request.characterId,
        update_fields=request.update_fields,
    )
    if modified_count is not None:
        return success_response(
            data=modified_count, message="Character updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No character was updated.")


sample_router = APIRouter(prefix="/sample", tags=["Sample"])


@sample_router.get("/", response_model=StandardResponse)
def get_sample_api(item_name: Optional[SampleItem] = None):
    if item_name is None:
        samples = {
            "relationship": domain_queries.get_relationship_sample(),
            "personality": domain_queries.get_personality_sample(),
            "long_term_goal": domain_queries.get_long_term_goal_sample(),
            "short_term_goal": domain_queries.get_short_term_goal_sample(),
            "language_style": domain_queries.get_language_style_sample(),
            "biography": domain_queries.get_biography_sample(),
        }
    else:
        sample_method = {
            SampleItem.relationship: domain_queries.get_relationship_sample,
            SampleItem.personality: domain_queries.get_personality_sample,
            SampleItem.long_term_goal: domain_queries.get_long_term_goal_sample,
            SampleItem.short_term_goal: domain_queries.get_short_term_goal_sample,
            SampleItem.language_style: domain_queries.get_language_style_sample,
            SampleItem.biography: domain_queries.get_biography_sample,
        }[item_name]

        samples = {item_name: sample_method()}
    if samples:
        return success_response(data=samples, message="Sample retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No sample found.")


agent_prompt_router = APIRouter(prefix="/agent_prompt", tags=["Agent Prompt"])


@agent_prompt_router.post("/", response_model=StandardResponse)
def store_agent_prompt_api(request: AgentPromptRequest):
    existing_prompt = retry_operation(
        domain_queries.get_agent_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
    )
    if existing_prompt:
        return JSONResponse(
            status_code=200,
            content={
                "code": 2,
                "message": f"Agent prompt for characterId {request.characterId} already exists.",
                "data": None,
            },
        )

    inserted_id = retry_operation(
        domain_queries.store_agent_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
        daily_goal=request.daily_goal,
        refer_to_previous=request.refer_to_previous,
        life_style=request.life_style,
        daily_objective_ar=request.daily_objective_ar,
        task_priority=request.task_priority,
        max_actions=request.max_actions,
        meta_seq_ar=request.meta_seq_ar,
        replan_time_limit=request.replan_time_limit,
        meta_seq_adjuster_ar=request.meta_seq_adjuster_ar,
        focus_topic=request.focus_topic,
        depth_of_reflection=request.depth_of_reflection,
        reflection_ar=request.reflection_ar,
        level_of_detail=request.level_of_detail,
        tone_and_style=request.tone_and_style,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Agent prompt stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store agent prompt.")


@agent_prompt_router.get("/", response_model=StandardResponse)
def get_agent_prompt_api(characterId: int):
    documents = retry_operation(
        domain_queries.get_agent_prompt,
        retries=3,
        delay=2,
        characterId=characterId,
    )
    if documents:
        return success_response(
            data=documents, message="Agent prompt retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No agent prompt found.")


@agent_prompt_router.put("/", response_model=StandardResponse)
def update_agent_prompt_api(request: UpdateAgentPromptRequest):
    result = retry_operation(
        domain_queries.update_agent_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
        update_fields=request.update_fields,
    )
    if result:
        return success_response(
            data=result, message="Agent prompt updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No agent prompt found to update.")


@agent_prompt_router.delete("/", response_model=StandardResponse)
def delete_agent_prompt_api(request: DeleteAgentPromptRequest):
    result = retry_operation(
        domain_queries.delete_agent_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
    )
    if result:
        return success_response(
            data=result, message="Agent prompt deleted successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No agent prompt found to delete.")


conversation_prompt_router = APIRouter(
    prefix="/conversation_prompt", tags=["Conversation Prompt"]
)


@conversation_prompt_router.post("/", response_model=StandardResponse)
def store_conversation_prompt_api(request: StoreConversationPromptRequest):
    existing_prompt = retry_operation(
        domain_queries.get_conversation_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
    )
    if existing_prompt:
        return JSONResponse(
            status_code=200,
            content={
                "code": 2,
                "message": f"Conversation prompt for characterId {request.characterId} already exists.",
                "data": None,
            },
        )

    inserted_id = retry_operation(
        domain_queries.store_conversation_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
        topic_requirements=request.topic_requirements,
        relation=request.relation,
        emotion=request.emotion,
        personality=request.personality,
        habits_and_preferences=request.habits_and_preferences,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Conversation prompt stored successfully."
        )
    else:
        raise HTTPException(
            status_code=500, detail="Failed to store conversation prompt."
        )


@conversation_prompt_router.get("/", response_model=StandardResponse)
def get_conversation_prompt_api(characterId: int):
    documents = retry_operation(
        domain_queries.get_conversation_prompt,
        retries=3,
        delay=2,
        characterId=characterId,
    )
    if documents:
        return success_response(
            data=documents, message="Conversation prompt retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No conversation prompt found.")


@conversation_prompt_router.put("/", response_model=StandardResponse)
def update_conversation_prompt_api(request: UpdateConversationPromptRequest):
    result = retry_operation(
        domain_queries.update_conversation_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
        update_fields=request.update_fields,
    )
    if result:
        return success_response(
            data=result, message="Conversation prompt updated successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No conversation prompt found to update."
        )


@conversation_prompt_router.delete("/", response_model=StandardResponse)
def delete_conversation_prompt_api(request: DeleteConversationPromptRequest):
    result = retry_operation(
        domain_queries.delete_conversation_prompt,
        retries=3,
        delay=2,
        characterId=request.characterId,
    )
    if result:
        return success_response(
            data=result, message="Conversation prompt deleted successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No conversation prompt found to delete."
        )


# 创建新的路由
decision_router = APIRouter(prefix="/decision", tags=["Decision"])


@decision_router.post("/", response_model=StandardResponse)
def store_decision_api(request: StoreDecisionRequest):
    inserted_id = retry_operation(
        domain_queries.store_decision,
        retries=3,
        delay=2,
        characterId=request.characterId,
        need_replan=request.need_replan,
        action_description=request.action_description,
        action_result=request.action_result,
        new_plan=request.new_plan,
        daily_objective=request.daily_objective,
        meta_seq=request.meta_seq,
        reflection=request.reflection,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Decision stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store decision.")


@decision_router.get("/", response_model=StandardResponse)
def get_decision_api(characterId: int, count: Optional[int] = None):
    decisions = retry_operation(
        domain_queries.get_decision,
        retries=3,
        delay=2,
        characterId=characterId,
        count=count,
    )
    if decisions:
        return success_response(
            data=decisions, message="Decisions retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No decisions found.")


# 创建新的路由
current_pointer_router = APIRouter(prefix="/current_pointer", tags=["Current Pointer"])


@current_pointer_router.post("/", response_model=StandardResponse)
def store_current_pointer_api(request: CurrentPointerRequest):
    inserted_id = retry_operation(
        domain_queries.store_current_pointer,
        retries=3,
        delay=2,
        characterId=request.characterId,
        current_pointer=request.current_pointer,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Current pointer stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store current pointer.")


@current_pointer_router.get("/{characterId}", response_model=StandardResponse)
def get_current_pointer_api(characterId: int):
    documents = retry_operation(
        domain_queries.get_current_pointer, retries=3, delay=2, characterId=characterId
    )
    if documents:
        return success_response(
            data=documents, message="Current pointer retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No current pointer found.")


@current_pointer_router.put("/", response_model=StandardResponse)
def update_current_pointer_api(request: CurrentPointerRequest):
    result = retry_operation(
        domain_queries.update_current_pointer,
        retries=3,
        delay=2,
        characterId=request.characterId,
        new_pointer=request.current_pointer,
    )
    if result:
        return success_response(
            data=result, message="Current pointer updated successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No current pointer found to update."
        )


@current_pointer_router.delete("/{characterId}", response_model=StandardResponse)
def delete_current_pointer_api(characterId: int):
    result = retry_operation(
        domain_queries.delete_current_pointer,
        retries=3,
        delay=2,
        characterId=characterId,
    )
    if result:
        return success_response(
            data=result, message="Current pointer deleted successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No current pointer found to delete."
        )


conversation_router = APIRouter(prefix="/conversation", tags=["Conversation"])


@conversation_router.get("/", response_model=StandardResponse)
def get_conversation_api(
    from_id: Optional[int] = None,
    to_id: Optional[int] = None,
    k: Optional[int] = None,
    start_day: Optional[int] = None,
    start_time: Optional[str] = None,
    characterId: Optional[int] = None,
):
    try:
        conversations = domain_queries.get_conversation(
            from_id=from_id,
            to_id=to_id,
            k=k,
            start_day=start_day,
            start_time=start_time,
            characterId=characterId,
        )
        if conversations:
            return success_response(
                data=conversations, message="Conversations retrieved successfully."
            )
        else:
            raise HTTPException(status_code=404, detail="No conversations found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@conversation_router.post("/by_list", response_model=StandardResponse)
def get_conversation_by_list_api(request: GetConversationByListRequest):
    try:
        conversations = domain_queries.get_conversation_by_list(
            characterIds=request.characterIds, time=request.time, k=request.k
        )
        if conversations:
            return success_response(
                data=conversations, message="Conversations retrieved successfully."
            )
        else:
            raise HTTPException(status_code=404, detail="No conversations found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@conversation_router.post("/", response_model=StandardResponse)
def store_conversation_api(request: StoreConversationRequest):
    try:
        inserted_id = domain_queries.store_conversation(
            from_id=request.from_id,
            to_id=request.to_id,
            start_time=request.start_time,
            start_day=request.start_day,
            message=request.message,
            send_gametime=request.send_gametime,
            send_realtime=request.send_realtime,
        )
        if inserted_id:
            return success_response(
                data=str(inserted_id), message="Conversation stored successfully."
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to store conversation.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


conversation_memory_router = APIRouter(
    prefix="/conversation_memory", tags=["Conversation Memory"]
)


@conversation_memory_router.post("/", response_model=StandardResponse)
def store_conversation_memory_api(request: StoreConversationMemoryRequest):
    inserted_id = retry_operation(
        domain_queries.store_conversation_memory,
        retries=3,
        delay=2,
        characterId=request.characterId,
        day=request.day,
        topic_plan=request.topic_plan,
        time_list=request.time_list,
        started=request.started,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Conversation memory stored successfully."
        )
    else:
        raise HTTPException(
            status_code=500, detail="Failed to store conversation memory."
        )


@conversation_memory_router.get("/", response_model=StandardResponse)
def get_conversation_memory_api(characterId: int, day: Optional[int] = None):
    documents = retry_operation(
        domain_queries.get_conversation_memory,
        retries=3,
        delay=2,
        characterId=characterId,
        day=day,
    )
    if documents:
        return success_response(
            data=documents, message="Conversation memory retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No conversation memory found.")


@conversation_memory_router.get("/memory", response_model=StandardResponse)
def get_memory_api(characterId: int, day: int, count: Optional[int] = 1):
    memory_data = retry_operation(
        domain_queries.get_memory,
        retries=3,
        delay=2,
        characterId=characterId,
        day=day,
        count=count,
    )
    if memory_data:
        return success_response(
            data=memory_data, message="Memory data retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No memory data found.")


@conversation_memory_router.put("/", response_model=StandardResponse)
def update_conversation_memory_api(request: UpdateConversationMemoryRequest):
    result = retry_operation(
        domain_queries.update_conversation_memory,
        retries=3,
        delay=2,
        characterId=request.characterId,
        day=request.day,
        update_fields=request.update_fields,
        add_started=request.add_started,
    )
    if result:
        return success_response(
            data=result, message="Conversation memory updated successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No conversation memory found to update."
        )


work_experience_router = APIRouter(prefix="/work_experience", tags=["Work Experience"])


@work_experience_router.post("/", response_model=StandardResponse)
def store_work_experience_api(request: StoreWorkExperienceRequest):
    inserted_id = retry_operation(
        domain_queries.store_work_experience,
        retries=3,
        delay=2,
        characterId=request.characterId,
        jobid=request.jobid,
        start_date=request.start_date,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Work experience stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store work experience.")


@work_experience_router.get("/all", response_model=StandardResponse)
def get_all_work_experiences_api(characterId: int):
    documents = retry_operation(
        domain_queries.get_all_work_experiences,
        retries=3,
        delay=2,
        characterId=characterId,
    )
    if documents:
        return success_response(
            data=documents, message="All work experiences retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No work experiences found.")


@work_experience_router.get("/current", response_model=StandardResponse)
def get_current_work_experience_api(characterId: int):
    document = retry_operation(
        domain_queries.get_current_work_experience,
        retries=3,
        delay=2,
        characterId=characterId,
    )
    if document:
        return success_response(
            data=document, message="Current work experience retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No current work experience found.")


@work_experience_router.put("/", response_model=StandardResponse)
def update_work_experience_api(request: UpdateWorkExperienceRequest):
    result = retry_operation(
        domain_queries.update_work_experience,
        retries=3,
        delay=2,
        characterId=request.characterId,
        jobid=request.jobid,
        additional_work=request.additional_work,
        additional_salary=request.additional_salary,
    )
    if result:
        return success_response(
            data=result, message="Work experience updated successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No work experience found to update."
        )


character_arc_router = APIRouter(prefix="/character_arc", tags=["Character Arc"])


@character_arc_router.post("/", response_model=StandardResponse)
def store_character_arc_api(request: StoreCharacterArcRequest):
    inserted_id = retry_operation(
        domain_queries.store_character_arc,
        retries=3,
        delay=2,
        characterId=request.characterId,
        belief=request.belief,
        mood=request.mood,
        values=request.values,
        habits=request.habits,
        personality=request.personality,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Character arc stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store character arc.")


@character_arc_router.get("/", response_model=StandardResponse)
def get_character_arc_api(characterId: int, k: Optional[int] = None):
    character_arcs = retry_operation(
        domain_queries.get_character_arc,
        retries=3,
        delay=2,
        characterId=characterId,
        k=k,
    )
    if character_arcs:
        return success_response(
            data=character_arcs, message="Character arcs retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No character arcs found.")


knowledge_graph_router = APIRouter(prefix="/knowledge_graph", tags=["Knowledge Graph"])


@knowledge_graph_router.get("/{character_id}", response_model=StandardResponse)
def get_knowledge_graph_api(character_id: int):
    try:
        knowledge_graph_data = domain_queries.get_knowledge_graph_data(character_id)
        return success_response(
            data=knowledge_graph_data,
            message="Knowledge graph data retrieved successfully.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(vector_search_router)
app.include_router(impressions_router)
app.include_router(cvs_router)
app.include_router(actions_router)
app.include_router(descriptors_router)
app.include_router(daily_objectives_router)
app.include_router(plans_router)
app.include_router(meta_sequences_router)
app.include_router(diaries_router)
app.include_router(characters_router)
app.include_router(encounter_count_router)
app.include_router(intimacy_router)
app.include_router(knowledge_router)
app.include_router(sample_router)
app.include_router(agent_prompt_router)
app.include_router(conversation_prompt_router)
app.include_router(decision_router)
app.include_router(crud_router)
app.include_router(current_pointer_router)
app.include_router(conversation_router)
app.include_router(conversation_memory_router)
app.include_router(work_experience_router)
app.include_router(character_arc_router)
app.include_router(knowledge_graph_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085)
