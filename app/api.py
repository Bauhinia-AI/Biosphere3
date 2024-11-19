# app/api.py
import logging
from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uvicorn
import sys
import os
import time

from pymongo.errors import PyMongoError, DuplicateKeyError

# Ensure the parent directory is in the Python path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo_utils import MongoDBUtils
from database.domain_specific_queries import DomainSpecificQueries

# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create logs directory in project root
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


# Define the standard response model
class StandardResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


# Utility functions for standardized responses
def success_response(data: Any, message: str = "Operation successful.") -> Dict:
    return {"code": 1, "message": message, "data": data}


def failure_response(message: str, data: Any = None) -> Dict:
    return {"code": 0, "message": message, "data": data}


# Initialize the database utility classes
try:
    db_utils = MongoDBUtils()
    domain_queries = DomainSpecificQueries(db_utils=db_utils)  # Pass db_utils here
    logging.info("Successfully initialized database utilities.")
except Exception as e:
    logging.critical(f"Failed to initialize database utilities: {e}")
    sys.exit(1)  # Exit the application if initialization fails


# Exception Handlers
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
    # Map HTTP status codes to custom messages
    status_messages = {
        400: "Bad request. The server could not understand the request due to invalid syntax.",
        401: "Unauthorized access. Authentication is required and has failed or has not been provided.",
        403: "Forbidden. You do not have permission to access this resource.",
        404: "Resource not found. The requested resource could not be found on the server.",
        405: "Method not allowed. The request method is not supported for the requested resource.",
        409: "Conflict error. The request could not be completed due to a conflict with the current state of the resource.",
        410: "Gone. The resource requested is no longer available and will not be available again.",
        413: "Payload too large. The request is larger than the server is willing or able to process.",
        415: "Unsupported media type. The request entity has a media type that the server or resource does not support.",
        422: "Unprocessable entity. The request was well-formed but was unable to be followed due to semantic errors.",
        429: "Too many requests. You have sent too many requests in a given amount of time.",
        500: "Internal server error. The server encountered an unexpected condition that prevented it from fulfilling the request.",
        501: "Not implemented. The server does not support the functionality required to fulfill the request.",
        502: "Bad gateway. The server received an invalid response from the upstream server.",
        503: "Service unavailable. The server is currently unable to handle the request due to temporary overload or maintenance.",
        504: "Gateway timeout. The server did not receive a timely response from the upstream server.",
        307: "Temporary redirect. The requested resource is temporarily available at a different URI.",
    }

    message = status_messages.get(
        exc.status_code,
        "An error occurred. Please refer to the specific error code for more details.",
    )
    return JSONResponse(status_code=200, content=failure_response(message=message))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Extract field names and error messages
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


# Define Pydantic models for request validation
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
    from_id: Optional[int] = None  # 将 from_id 设置为可选
    to_id: Optional[int] = None  # 将 to_id 设置为可选
    intimacy_level_min: Optional[int] = None  # 新增字段，用于指定亲密度的最小值
    intimacy_level_max: Optional[int] = None  # 新增字段，用于指定亲密度的最大值


class StoreIntimacyRequest(BaseModel):
    from_id: int
    to_id: int
    intimacy_level: Optional[int] = 50


class UpdateIntimacyRequest(BaseModel):
    from_id: int
    to_id: int
    new_intimacy_level: int


class ConversationsWithcharactersRequest(BaseModel):
    characterIds_list: List[int]
    k: Optional[int] = 1


class ConversationsContainingcharacterRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class StoreConversationRequest(BaseModel):
    characterIds: List[int]
    dialogue: List[Dict[str, str]]
    start_day: int  # 新增字段
    start_time: str  # 新增字段


class GetConversationByIdDayTimeRequest(BaseModel):
    characterIds_list: List[int]  # 更新为角色ID列表
    day: int
    time: str


class GetConversationsByIdAndDayRequest(BaseModel):
    characterId: int
    day: int


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
    week: int  # 新增字段
    election_result: Optional[str] = (
        "not_yet"  # 选举状态, 可以为 'not_yet'（未进行选举）、'failed'（选举失败）、'succeeded'（选举成功），默认值为 "not_yet"
    )


class UpdateElectionResultRequest(BaseModel):
    characterId: int
    election_result: str
    jobid: Optional[int] = None
    week: Optional[int] = None


class GetCVRequest(BaseModel):
    jobid: Optional[int] = None
    characterId: Optional[int] = None
    week: Optional[int] = None  # 新增字段，设置为可选
    election_result: Optional[str] = None  # 新增字段，设置为可选


class StoreActionRequest(BaseModel):
    characterId: int
    action: str
    result: Dict
    description: str


class GetActionRequest(BaseModel):
    characterId: int
    action: str
    k: Optional[int] = 1


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


class StoreToolRequest(BaseModel):
    API: str
    text: str
    code: str


class GetToolsRequest(BaseModel):
    API: Optional[str] = None
    k: Optional[int] = 1


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
    characterList: List[int]  # 角色ID列表
    topic: str
    k: Optional[int] = 1


class UpdatecharacterRequest(BaseModel):
    characterId: int
    update_fields: dict


class CharacterArcRequest(BaseModel):
    characterId: int
    category: List[Dict[str, str]]


class CharacterArcChangeRequest(BaseModel):
    characterId: int
    item: str
    cause: str
    context: str
    change: str


class GetCharacterArcRequest(BaseModel):
    characterId: int


class GetCharacterArcWithChangesRequest(BaseModel):
    characterId: int
    k: Optional[int] = 1


class UpdateCharacterArcRequest(BaseModel):
    characterId: int
    category: List[Dict[str, str]]


class GetCharacterArcChangesRequest(BaseModel):
    characterId: int
    item: str
    k: Optional[int] = 1


# Utility function for retrying operations
def retry_operation(func, retries=3, delay=2, *args, **kwargs):
    """Utility function to retry an operation, skipping retries for DuplicateKeyError."""
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except DuplicateKeyError as e:
            # If DuplicateKeyError occurs, do not retry
            logging.info(f"Duplicate key error: {e}")
            raise e  # Let the global handler catch it
        except PyMongoError as e:
            logging.error(f"PyMongoError on attempt {attempt}: {e}")
            if attempt < retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.critical(f"Operation failed after {retries} attempts.")
                raise e  # Let the global handler catch it
        except Exception as e:
            logging.error(f"Unexpected error on attempt {attempt}: {e}")
            if attempt < retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.critical(
                    f"Operation failed after {retries} attempts due to unexpected error."
                )
                raise e  # Let the global handler catch it


# Define APIRouters for categorization

# CRUD Operations Router
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


@crud_router.post("/update", response_model=StandardResponse)
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


@crud_router.post("/delete", response_model=StandardResponse)
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


@crud_router.post("/find", response_model=StandardResponse)
def find_data(request: FindRequest):
    documents = retry_operation(
        db_utils.find_documents,
        retries=3,
        delay=2,
        collection_name=request.collection_name,
        query=request.query,
        projection=request.projection,
        limit=request.limit,
        sort=request.sort,
    )
    if documents:
        return success_response(
            data=documents, message="Documents retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No documents found.")


# Vector Search Router
vector_search_router = APIRouter(
    prefix="/vector_search", tags=["Vector Search"]
)  # 添加 tags 参数


@vector_search_router.post("/", response_model=StandardResponse)
def vector_search_api(request: VectorSearchRequest):
    results = retry_operation(
        domain_queries.vector_search,
        retries=3,
        delay=2,
        collection_name=request.collection_name,
        query_text=request.query_text,
        fields_to_return=request.fields_to_return,
        k=request.k,
    )
    if results:
        return success_response(
            data=results, message="Vector search completed successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No results found for the vector search."
        )


# Impressions Router
impressions_router = APIRouter(
    prefix="/impressions", tags=["Impressions"]
)  # 添加 tags 参数


@impressions_router.post("/get", response_model=StandardResponse)
def get_impression_api(request: ImpressionRequest):
    impressions = retry_operation(
        domain_queries.get_impression_from_mongo,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
        k=request.k,
    )
    if impressions:
        return success_response(
            data=impressions, message="Impressions retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No impressions found.")


@impressions_router.post("/store", response_model=StandardResponse)
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


# Intimacy Router
intimacy_router = APIRouter(prefix="/intimacy", tags=["Intimacy"])  # 添加 tags 参数


@intimacy_router.post("/get", response_model=StandardResponse)
def get_intimacy_api(request: IntimacyRequest):
    intimacy = retry_operation(
        domain_queries.get_intimacy,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
        intimacy_level_min=request.intimacy_level_min,  # 新增参数
        intimacy_level_max=request.intimacy_level_max,  # 新增参数
    )
    if intimacy:
        return success_response(
            data=intimacy, message="Intimacy level retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No intimacy level found.")


@intimacy_router.post("/store", response_model=StandardResponse)
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


@intimacy_router.post("/update", response_model=StandardResponse)
def update_intimacy_api(request: UpdateIntimacyRequest):
    # 尝试获取当前的好感度记录
    current_intimacy = retry_operation(
        domain_queries.get_intimacy,
        retries=3,
        delay=2,
        from_id=request.from_id,
        to_id=request.to_id,
    )

    if current_intimacy:
        # 更新好感度为请求中提供的新值
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


@intimacy_router.post("/decrease_all", response_model=StandardResponse)
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


# Conversations Router
conversations_router = APIRouter(
    prefix="/conversations", tags=["Conversations"]
)  # 添加 tags 参数


@conversations_router.post("/get_with_characterIds", response_model=StandardResponse)
def get_conversations_with_characterIds_api(
    request: ConversationsWithcharactersRequest,
):
    conversations = retry_operation(
        domain_queries.get_conversations_with_characterIds,
        retries=3,
        delay=2,
        characterIds_list=request.characterIds_list,
        k=request.k,
    )
    if conversations:
        return success_response(
            data=conversations, message="Conversations retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No conversations found.")


@conversations_router.post(
    "/get_containing_characterId", response_model=StandardResponse
)
def get_conversations_containing_characterId_api(
    request: ConversationsContainingcharacterRequest,
):
    conversations = retry_operation(
        domain_queries.get_conversations_containing_characterId,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if conversations:
        return success_response(
            data=conversations, message="Conversations retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No conversations found.")


@conversations_router.post("/store", response_model=StandardResponse)
def store_conversation_api(request: StoreConversationRequest):
    inserted_id = retry_operation(
        domain_queries.store_conversation,
        retries=3,
        delay=2,
        characterIds=request.characterIds,
        dialogue=request.dialogue,
        start_day=request.start_day,  # 新增字段
        start_time=request.start_time,  # 新增字段
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Conversation stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store conversation.")


@conversations_router.post("/get_by_id_day_time", response_model=StandardResponse)
def get_conversation_by_id_day_time_api(request: GetConversationByIdDayTimeRequest):
    conversations = retry_operation(
        domain_queries.get_conversation_by_id_day_time,
        retries=3,
        delay=2,
        characterIds_list=request.characterIds_list,  # 更新为 characterIds_list
        day=request.day,
        time=request.time,
    )
    if conversations:
        return success_response(
            data=conversations, message="Conversation retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No conversation found.")


@conversations_router.post("/get_by_id_and_day", response_model=StandardResponse)
def get_conversations_by_id_and_day_api(request: GetConversationsByIdAndDayRequest):
    conversations = retry_operation(
        domain_queries.get_conversations_by_id_and_day,
        retries=3,
        delay=2,
        characterId=request.characterId,
        day=request.day,
    )
    if conversations:
        return success_response(
            data=conversations, message="Conversations retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No conversations found.")


# Encounter Count Router
encounter_count_router = APIRouter(
    prefix="/encounter_count", tags=["Encounter Count"]
)  # 添加 tags 参数


# 修改 `get_encounter_count_api` 方法的请求参数类型
@encounter_count_router.post("/get", response_model=StandardResponse)
def get_encounter_count_api(
    request: EncounterCountRequest,
):  # 修改为 EncounterCountRequest
    encounter_count = retry_operation(
        domain_queries.get_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,  # 修改为 from_id
        to_id=request.to_id,  # 修改为 to_id
    )
    if encounter_count:
        return success_response(
            data=encounter_count, message="Encounter count retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No encounter count found.")


# Define the API for getting encounters by from_id
@encounter_count_router.post("/get_by_from_id", response_model=StandardResponse)
def get_encounter_count_by_from_id_api(request: GetEncountersByFromIdRequest):
    encounters = retry_operation(
        domain_queries.get_encounters_by_from_id,
        retries=3,
        delay=2,
        from_id=request.from_id,  # Use from_id from the request
        k=request.k,  # Use k from the request to limit results
    )
    if encounters:
        return success_response(
            data=encounters, message="Encounters retrieved successfully."
        )
    else:
        raise HTTPException(
            status_code=404, detail="No encounters found for the specified from_id."
        )


# 修改 `store_encounter_count_api` 方法的请求参数
@encounter_count_router.post("/store", response_model=StandardResponse)
def store_encounter_count_api(request: StoreEncounterCountRequest):
    inserted_id = retry_operation(
        domain_queries.store_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,  # 修改为 from_id
        to_id=request.to_id,  # 修改为 to_id
        count=request.count,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Encounter count stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store encounter count.")


# 修改 `increment_encounter_count_api` 方法的请求参数
@encounter_count_router.post("/increment", response_model=StandardResponse)
def increment_encounter_count_api(request: EncounterCountRequest):
    current_count = retry_operation(
        domain_queries.get_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,  # 修改为 from_id
        to_id=request.to_id,  # 修改为 to_id
    )
    if current_count:
        new_count = current_count[0]["count"] + 1
        result = retry_operation(
            domain_queries.update_encounter_count,
            retries=3,
            delay=2,
            from_id=request.from_id,  # 修改为 from_id
            to_id=request.to_id,  # 修改为 to_id
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
        # 如果 current_count 不存在，则新建一条记录
        inserted_id = retry_operation(
            domain_queries.store_encounter_count,
            retries=3,
            delay=2,
            from_id=request.from_id,  # 修改为 from_id
            to_id=request.to_id,  # 修改为 to_id
            count=1,  # 新建记录时，count 设置为 1
        )
        if inserted_id:
            return success_response(
                data=str(inserted_id), message="Encounter count created and set to 1."
            )
        else:
            raise HTTPException(
                status_code=500, detail="Failed to create encounter count."
            )


# 修改 `update_encounter_count_api` 方法的请求参数
@encounter_count_router.post("/update", response_model=StandardResponse)
def update_encounter_count_api(request: UpdateEncounterCountRequest):
    result = retry_operation(
        domain_queries.update_encounter_count,
        retries=3,
        delay=2,
        from_id=request.from_id,  # 修改为 from_id
        to_id=request.to_id,  # 修改为 to_id
        new_count=request.count,
    )
    if result:
        return success_response(
            data=result, message="Encounter count updated successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to update encounter count.")


# CVs Router
cvs_router = APIRouter(prefix="/cv", tags=["CVs"])  # 添加 tags 参数


@cvs_router.post("/store", response_model=StandardResponse)
def store_cv_api(request: StoreCVRequest):
    inserted_id = retry_operation(
        domain_queries.store_cv,
        retries=3,
        delay=2,
        jobid=request.jobid,
        characterId=request.characterId,
        CV_content=request.CV_content,
        week=request.week,  # 传递 week 参数
        election_result=request.election_result,  # 传递 election_result 参数
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="CV stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store CV.")


@cvs_router.post("/update_election_result", response_model=StandardResponse)
def update_election_result_api(request: UpdateElectionResultRequest):
    result = retry_operation(
        domain_queries.update_election_result,
        retries=3,
        delay=2,
        characterId=request.characterId,
        election_result=request.election_result,
        jobid=request.jobid,
        week=request.week,
    )
    if result:
        return success_response(
            data=result, message="Election result updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No CV found to update.")


@cvs_router.post("/get", response_model=StandardResponse)
def get_cv_api(request: GetCVRequest):
    cvs = retry_operation(
        domain_queries.get_cv,
        retries=3,
        delay=2,
        jobid=request.jobid,
        characterId=request.characterId,
        week=request.week,  # 传递 week 参数
        election_result=request.election_result,  # 传递 election_result 参数
    )
    if cvs:
        return success_response(data=cvs, message="CVs retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No CVs found.")


# Actions Router
actions_router = APIRouter(prefix="/actions", tags=["Actions"])  # 添加 tags 参数


@actions_router.post("/store", response_model=StandardResponse)
def store_action_api(request: StoreActionRequest):
    inserted_id = retry_operation(
        domain_queries.store_action,
        retries=3,
        delay=2,
        characterId=request.characterId,
        action=request.action,
        result=request.result,
        description=request.description,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Action stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store action.")


@actions_router.post("/get", response_model=StandardResponse)
def get_action_api(request: GetActionRequest):
    actions = retry_operation(
        domain_queries.get_action,
        retries=3,
        delay=2,
        characterId=request.characterId,
        action=request.action,
        k=request.k,
    )
    if actions:
        return success_response(data=actions, message="Actions retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No actions found.")


# Descriptors Router
descriptors_router = APIRouter(
    prefix="/descriptors", tags=["Descriptors"]
)  # 添加 tags 参数


@descriptors_router.post("/store", response_model=StandardResponse)
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


@descriptors_router.post("/get", response_model=StandardResponse)
def get_descriptor_api(request: GetDescriptorRequest):
    descriptors = retry_operation(
        domain_queries.get_descriptor,
        retries=3,
        delay=2,
        action_id=request.action_id,
        characterId=request.characterId,
        k=request.k,
    )
    if descriptors:
        return success_response(
            data=descriptors, message="Descriptors retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No descriptors found.")


# Daily Objectives Router
daily_objectives_router = APIRouter(
    prefix="/daily_objectives", tags=["Daily Objectives"]
)  # 添加 tags 参数


@daily_objectives_router.post("/store", response_model=StandardResponse)
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


@daily_objectives_router.post("/get", response_model=StandardResponse)
def get_daily_objectives_api(request: GetDailyObjectivesRequest):
    objectives = retry_operation(
        domain_queries.get_daily_objectives,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if objectives:
        return success_response(
            data=objectives, message="Daily objectives retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No daily objectives found.")


# Plans Router
plans_router = APIRouter(prefix="/plans", tags=["Plans"])  # 添加 tags 参数


@plans_router.post("/store", response_model=StandardResponse)
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


@plans_router.post("/get", response_model=StandardResponse)
def get_plans_api(request: GetPlansRequest):
    plans = retry_operation(
        domain_queries.get_plans,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if plans:
        return success_response(data=plans, message="Plans retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No plans found.")


# Meta Sequences Router
meta_sequences_router = APIRouter(
    prefix="/meta_sequences", tags=["Meta Sequences"]
)  # 添加 tags 参数


@meta_sequences_router.post("/store", response_model=StandardResponse)
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


@meta_sequences_router.post("/get", response_model=StandardResponse)
def get_meta_sequences_api(request: GetMetaSequencesRequest):
    meta_sequences = retry_operation(
        domain_queries.get_meta_sequences,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if meta_sequences:
        return success_response(
            data=meta_sequences, message="Meta sequences retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No meta sequences found.")


@meta_sequences_router.post("/update", response_model=StandardResponse)
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


# Knowledge Router
knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge"])  # 添加 tags 参数


@knowledge_router.post("/store", response_model=StandardResponse)
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


@knowledge_router.post("/get", response_model=StandardResponse)
def get_knowledge_api(request: GetKnowledgeRequest):
    knowledge = retry_operation(
        domain_queries.get_knowledge,
        retries=3,
        delay=2,
        characterId=request.characterId,
        day=request.day,
    )
    if knowledge:
        return success_response(
            data=knowledge, message="Knowledge retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No knowledge found.")


@knowledge_router.post("/get_latest", response_model=StandardResponse)
def get_latest_knowledge_api(request: GetLatestKnowledgeRequest):
    knowledge = retry_operation(
        domain_queries.get_latest_knowledge,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if knowledge:
        return success_response(
            data=knowledge, message="Latest knowledge retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No latest knowledge found.")


@knowledge_router.post("/update", response_model=StandardResponse)
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


# Tools Router
tools_router = APIRouter(prefix="/tools", tags=["Tools"])  # 添加 tags 参数


@tools_router.post("/store", response_model=StandardResponse)
def store_tool_api(request: StoreToolRequest):
    inserted_id = retry_operation(
        domain_queries.store_tool,
        retries=3,
        delay=2,
        API=request.API,
        text=request.text,
        code=request.code,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Tool stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store tool.")


@tools_router.post("/get", response_model=StandardResponse)
def get_tools_api(request: GetToolsRequest):
    tools = retry_operation(
        domain_queries.get_tools, retries=3, delay=2, API=request.API, k=request.k
    )
    if tools:
        return success_response(data=tools, message="Tools retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No tools found.")


# Diaries Router
diaries_router = APIRouter(prefix="/diaries", tags=["Diaries"])  # 添加 tags 参数


@diaries_router.post("/store", response_model=StandardResponse)
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


@diaries_router.post("/get", response_model=StandardResponse)
def get_diaries_api(request: GetDiariesRequest):
    diaries = retry_operation(
        domain_queries.get_diaries,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if diaries:
        return success_response(data=diaries, message="Diaries retrieved successfully.")
    else:
        raise HTTPException(status_code=404, detail="No diaries found.")


# Characters Router
characters_router = APIRouter(
    prefix="/characters", tags=["Characters"]
)  # 添加 tags 参数


@characters_router.post("/store", response_model=StandardResponse)
def store_character_api(request: StorecharacterRequest):
    # Check if character with the given characterId already exists
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

    character_data = {
        "characterId": request.characterId,
        "characterName": request.characterName,
        "gender": request.gender,
        "relationship": request.relationship,
        "personality": request.personality,
        "long_term_goal": request.long_term_goal,
        "short_term_goal": request.short_term_goal,
        "language_style": request.language_style,
        "biography": request.biography,
    }

    # 删除值为 None 的字段
    character_data = {k: v for k, v in character_data.items() if v is not None}

    # Proceed to store the character with filtered data
    inserted_id = retry_operation(
        domain_queries.store_character, retries=3, delay=2, **character_data
    )

    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Character stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store character.")


@characters_router.post("/get", response_model=StandardResponse)
def get_character_api(request: GetcharacterRequest):
    characters = retry_operation(
        domain_queries.get_character,
        retries=3,
        delay=2,
        characterId=request.characterId,  # characterId 可以为 None
    )
    if characters:
        return success_response(
            data=characters, message="Characters retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No characters found.")


@characters_router.post("/get_rag", response_model=StandardResponse)
def get_character_rag_api(request: characterRAGRequest):
    character_rag_results = retry_operation(
        domain_queries.get_character_RAG,
        retries=3,
        delay=2,
        characterId=request.characterId,
        topic=request.topic,
        k=request.k,
    )
    if character_rag_results:
        return success_response(
            data=character_rag_results,
            message="Character RAG results retrieved successfully.",
        )
    else:
        raise HTTPException(status_code=404, detail="No character RAG results found.")


@characters_router.post("/get_rag_in_list", response_model=StandardResponse)
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


@characters_router.post("/update", response_model=StandardResponse)
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


character_arc_router = APIRouter(
    prefix="/character_arc", tags=["Character Arc"]
)  # 添加 tags 参数


@character_arc_router.post("/store", response_model=StandardResponse)
def store_character_arc_api(request: CharacterArcRequest):
    inserted_id = retry_operation(
        domain_queries.store_character_arc,
        retries=3,
        delay=2,
        characterId=request.characterId,
        category=request.category,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Character arc stored successfully."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to store character arc.")


@character_arc_router.post("/get", response_model=StandardResponse)
def get_character_arc_api(request: GetCharacterArcRequest):
    arc = retry_operation(
        domain_queries.get_character_arc,
        retries=3,
        delay=2,
        characterId=request.characterId,
    )
    if arc:
        return success_response(
            data=arc, message="Character arc retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No character arc found.")


@character_arc_router.post("/get_with_changes", response_model=StandardResponse)
def get_character_arc_with_changes_api(request: GetCharacterArcWithChangesRequest):
    arc_with_changes = retry_operation(
        domain_queries.get_character_arc_with_changes,
        retries=3,
        delay=2,
        characterId=request.characterId,
        k=request.k,
    )
    if arc_with_changes:
        return success_response(
            data=arc_with_changes,
            message="Character arc with changes retrieved successfully.",
        )
    else:
        raise HTTPException(
            status_code=404, detail="No character arc with changes found."
        )


@character_arc_router.post("/update", response_model=StandardResponse)
def update_character_arc_api(request: UpdateCharacterArcRequest):
    result = retry_operation(
        domain_queries.update_character_arc,
        retries=3,
        delay=2,
        characterId=request.characterId,
        category=request.category,
    )
    if result:
        return success_response(
            data=result, message="Character arc updated successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No character arc was updated.")


@character_arc_router.post("/store_change", response_model=StandardResponse)
def store_character_arc_change_api(request: CharacterArcChangeRequest):
    inserted_id = retry_operation(
        domain_queries.store_character_arc_change,
        retries=3,
        delay=2,
        characterId=request.characterId,
        item=request.item,
        cause=request.cause,
        context=request.context,
        change=request.change,
    )
    if inserted_id:
        return success_response(
            data=str(inserted_id), message="Character arc change stored successfully."
        )
    else:
        raise HTTPException(
            status_code=500, detail="Failed to store character arc change."
        )


@character_arc_router.post("/get_changes", response_model=StandardResponse)
def get_character_arc_changes_api(request: GetCharacterArcChangesRequest):
    changes = retry_operation(
        domain_queries.get_character_arc_changes,
        retries=3,
        delay=2,
        characterId=request.characterId,
        item=request.item,
        k=request.k,
    )
    if changes:
        return success_response(
            data=changes, message="Character arc changes retrieved successfully."
        )
    else:
        raise HTTPException(status_code=404, detail="No character arc changes found.")


# Include all routers into the main app
app.include_router(crud_router)
app.include_router(vector_search_router)
app.include_router(impressions_router)
app.include_router(conversations_router)
app.include_router(cvs_router)
app.include_router(actions_router)
app.include_router(descriptors_router)
app.include_router(daily_objectives_router)
app.include_router(plans_router)
app.include_router(meta_sequences_router)
app.include_router(tools_router)
app.include_router(diaries_router)
app.include_router(characters_router)
app.include_router(encounter_count_router)
app.include_router(intimacy_router)
app.include_router(knowledge_router)
app.include_router(character_arc_router)

# Start the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8085)
