# test_client.py
from client import APIClient


def run_tests():
    client = APIClient(base_url="http://localhost:8085")

    # # 测试存储CV
    # print("=== 测试存储CV ===")
    # store_response = client.store_cv(
    #     jobid=1,
    #     characterId=200,
    #     CV_content="这是一个测试CV内容",
    #     week=1,
    #     health=100,
    #     studyxp=50,
    #     date=20231001,  # 将日期改为整数格式
    #     jobName="测试职位",
    #     election_status="not_yet",
    # )
    # print("存储CV响应:", store_response)

    # # 测试获取CV
    # print("=== 测试获取CV ===")
    # get_response = client.get_cv()
    # print("获取CV响应:", get_response)

    # print("=== 测试插入与查找数据 ===")
    # document = {
    #     "characterId": 200,
    #     "characterName": "Test User",
    #     "gender": "Non-binary",
    #     "slogan": "Testing insert_data",
    #     "description": "This is a test character inserted via insert_data.",
    #     "role": "Tester",
    #     "task": "Testing API endpoints",
    # }

    # # 测试插入数据
    # insert_resp = client.insert_data("character", document)
    # print("Inserting Data:", insert_resp)

    # # 测试查找数据
    # find_resp = client.find_data("character", {"characterId": 200})
    # print("Finding Data:", find_resp)

    # # 测试更新数据
    # update_query = {"characterId": 200}
    # update_fields = {"$set": {"characterName": "Updated Test User"}}
    # update_resp = client.update_data("character", update_query, update_fields)
    # print("Updating Data:", update_resp)

    # # 测试更新后查找
    # find_updated_resp = client.find_data("character", {"characterId": 200})
    # print("Finding Updated Data:", find_updated_resp)

    # # 测试删除数据
    # delete_resp = client.delete_data("npc", {"characterId": 103})
    # print("Deleting Data:", delete_resp)

    # # 测试删除后查找
    # find_deleted_resp = client.find_data("character", {"characterId": 200})
    # print("Finding Deleted Data:", find_deleted_resp)

    # print("\n=== 测试角色存储和检索 ===")
    # character_data = {
    #     "characterId": 102,
    #     "characterName": "Diana",
    #     "gender": "Female",
    # }
    # store_char_resp = client.store_character(**character_data)
    # print("Storing character:", store_char_resp)

    # get_char_resp = client.get_character(102)
    # print("Retrieving character:", get_char_resp)

    # print("\n=== 测试 Conversations ===")
    # conversation_data = {
    #     "characterIds": [2, 3],
    #     "dialogue": [
    #         {"Bob": "Hello"},
    #         {"Alice": "Hi Bob!"},
    #     ],
    #     "start_day": 2,
    #     "start_time": "09:00:00",
    # }
    # store_conv_resp = client.store_conversation(**conversation_data)
    # print("Storing Conversation:", store_conv_resp)

    # get_conv_resp = client.get_conversations_by_id_and_day(characterId=2, day=2)
    # print("Retrieving Conversations by ID and Day:", get_conv_resp)

    # print("\n=== 测试 Impressions ===")
    # impression_data = {"from_id": 1, "to_id": 2, "impression": "Test Impression"}
    # store_imp_resp = client.store_impression(**impression_data)
    # print("Storing Impression:", store_imp_resp)

    # get_imp_resp = client.get_impression(1, 2, k=1)
    # print("Retrieving Impression:", get_imp_resp)

    # print("\n=== 测试 Vector Search ===")
    # vector_search_data = {
    #     "query_text": "学习",
    #     "fields_to_return": ["characterId", "characterName"],
    #     "collection_name": "agent_profile",
    #     "k": 5,
    # }
    # vec_search_resp = client.vector_search(**vector_search_data)
    # print("Vector Search:", vec_search_resp)

    # print("\n=== 测试 Agent Prompt ===")
    # agent_prompt_data = {
    #     "characterId": 101,
    #     "daily_goal": "sleep well",
    #     "refer_to_previous": True,
    #     "life_style": "Busy",
    #     "max_actions": 5,
    #     "depth_of_reflection": "Deep",
    #     "level_of_detail": "Shallow",
    #     "tone_and_style": "Gentle",
    # }
    # store_agent_prompt_resp = client.store_agent_prompt(**agent_prompt_data)
    # print("Storing Agent Prompt:", store_agent_prompt_resp)

    # get_agent_prompt_resp = client.get_agent_prompt(101)
    # print("Retrieving Agent Prompt:", get_agent_prompt_resp)

    # update_agent_prompt_resp = client.update_agent_prompt(
    #     101, {"daily_goal": "updated goal"}
    # )
    # print("Updating Agent Prompt:", update_agent_prompt_resp)

    # delete_agent_prompt_resp = client.delete_agent_prompt(101)
    # print("Deleting Agent Prompt:", delete_agent_prompt_resp)

    # print("\n=== 测试 Conversation Prompt ===")
    # conversation_prompt_data = {
    #     "characterId": 101,
    #     "topic_requirements": "Discuss future plans",
    #     "relation": "Friendly",
    #     "emotion": "Happy",
    #     "personality": "Extraversion",
    #     "habits_and_preferences": "Enjoys hiking",
    # }
    # store_conv_prompt_resp = client.store_conversation_prompt(
    #     **conversation_prompt_data
    # )
    # print("Storing Conversation Prompt:", store_conv_prompt_resp)

    # get_conv_prompt_resp = client.get_conversation_prompt(101)
    # print("Retrieving Conversation Prompt:", get_conv_prompt_resp)

    # update_conv_prompt_resp = client.update_conversation_prompt(
    #     101, {"emotion": "Excited"}
    # )
    # print("Updating Conversation Prompt:", update_conv_prompt_resp)

    # delete_conv_prompt_resp = client.delete_conversation_prompt(101)
    # print("Deleting Conversation Prompt:", delete_conv_prompt_resp)

    # print("\n=== 测试 Sample ===")
    # sample_resp = client.get_sample()
    # print("Retrieving All Samples:", sample_resp)
    # sample_personality_resp = client.get_sample(item_name="personality")
    # print("Retrieving Personality Sample:", sample_personality_resp)


if __name__ == "__main__":
    run_tests()
