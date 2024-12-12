import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# MongoDB Configuration
db_name = "bio3agent"
# db_name = "biosphere3_test"
cv_collection_name = "cv"
agent_profile_collection_name = "agent_profile"
action_collection_name = "action"
impression_collection_name = "impression"
descriptor_collection_name = "descriptor"
daily_objective_collection_name = "daily_objective"
plan_collection_name = "plan"
meta_seq_collection_name = "meta_seq"
conversation_collection_name = "conversation"
diary_collection_name = "diary"
encounter_count_collection_name = "encounter_count"
intimacy_collection_name = "intimacy"
knowledge_collection_name = "knowledge"
character_arc_collection_name = "character_arc"
character_arc_change_collection_name = "character_arc_change"
profile_sample_collection_name = "profile_sample"
agent_prompt_collection_name = "agent_prompt"
conversation_prompt_collection_name = "conversation_prompt"
decision_collection_name = "decision"
current_pointer_collection_name = "current_pointer"

mongo_uri = os.getenv("MONGO_URI")
index_name = "vector_index"

# Model and API Configuration
api_key = os.getenv("API_KEY")
base_url = "https://api.aiproxy.io/v1"
model_name = "text-embedding-3-small"  # OpenAI Model
num_dimensions = 1536  # Dimensions for OpenAI model
limit = 5
similarity = "euclidean"
numCandidates = 1000

# 定义需要进行嵌入的集合及其对应的文本字段
RAG_COLLECTIONS = {
    # conversation_collection_name: "dialogue",
    agent_profile_collection_name: "full_profile",
    # 可以在此添加更多需要嵌入的集合和对应的字段
}
