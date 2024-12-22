# test_all_endpoints.py

import asyncio
from database_api_utils import make_api_request_sync
import json
import time


def test_crud_insert():
    print("Testing CRUD Insert...")
    insert_data = {
        "collection_name": "npc",
        "document": {
            "characterId": 103,
            "characterName": "Ethan",
            "gender": "Male",
            "spriteId": 1,
            "relationship": "Warrior",
            "personality": "Brave and loyal",
            "long_term_goal": "Defend the kingdom with unwavering courage",
            "short_term_goal": "Train daily to enhance combat skills",
            "language_style": "Direct and assertive",
            "biography": "A fearless warrior dedicated to protecting the realm.",
        },
    }
    response = make_api_request_sync("POST", "/crud/insert", data=insert_data)
    print(json.dumps(response, indent=4))


def test_crud_update():
    print("Testing CRUD Update...")
    # Ensure the document exists before updating
    # Insert the document if it does not exist
    insert_data = {
        "collection_name": "npc",
        "document": {
            "characterId": 104,
            "characterName": "Lily",
            "gender": "Female",
            "spriteId": 2,
            "relationship": "Healer",
            "personality": "Compassionate and wise",
            "long_term_goal": "Heal the lands and its inhabitants",
            "short_term_goal": "Gather medicinal herbs",
            "language_style": "Calm and soothing",
            "biography": "A dedicated healer with a deep understanding of nature.",
        },
    }
    # Insert if not exists
    make_api_request_sync("POST", "/crud/insert", data=insert_data)

    update_data = {
        "collection_name": "npc",
        "query": {"characterId": 104},
        "update": {"$set": {"personality": "Compassionate, wise, and resilient"}},
        "upsert": False,
        "multi": False,
    }
    response = make_api_request_sync("PUT", "/crud/update", data=update_data)
    print(json.dumps(response, indent=4))


def test_crud_delete():
    print("Testing CRUD Delete...")
    delete_data = {
        "collection_name": "npc",
        "query": {"characterId": 103},
        "multi": False,
    }
    response = make_api_request_sync("DELETE", "/crud/delete", data=delete_data)
    print(json.dumps(response, indent=4))


def test_crud_find():
    print("Testing CRUD Find...")
    find_params = {
        "collection_name": "npc",
        "query": {"gender": "Female"},
        "projection": {"_id": 0, "characterName": 1, "gender": 1},
        "limit": 10,
        "sort": {"characterName": 1},
    }
    response = make_api_request_sync("GET", "/crud/find", params=find_params)
    print(json.dumps(response, indent=4))


def test_vector_search():
    print("Testing Vector Search...")
    vector_search_params = {
        "query_text": "探索生活习惯",
        "fields_to_return": ["characterIds", "dialogue"],
        "collection_name": "conversation",
        "k": 5,
    }
    response = make_api_request_sync(
        "GET", "/vector_search/", params=vector_search_params
    )
    print(json.dumps(response, indent=4))


def test_impressions_get():
    print("Testing Impressions Get...")
    # Ensure that impressions exist before getting
    # Insert an impression if it does not exist
    store_impression_data = {
        "from_id": 101,
        "to_id": 102,
        "impression": "Friendly and helpful.",
    }
    make_api_request_sync("POST", "/impressions/", data=store_impression_data)

    impression_params = {"from_id": 101, "to_id": 102, "k": 3}
    response = make_api_request_sync("GET", "/impressions/", params=impression_params)
    print(json.dumps(response, indent=4))


def test_impressions_store():
    print("Testing Impressions Store...")
    store_impression_data = {
        "from_id": 101,
        "to_id": 103,
        "impression": "Respectful and supportive.",
    }
    response = make_api_request_sync(
        "POST", "/impressions/", data=store_impression_data
    )
    print(json.dumps(response, indent=4))


def test_intimacy_get():
    print("Testing Intimacy Get...")
    # Ensure intimacy data exists before getting
    store_intimacy_data = {"from_id": 101, "to_id": 102, "intimacy_level": 40}
    make_api_request_sync("POST", "/intimacy/", data=store_intimacy_data)

    intimacy_params = {
        "from_id": 101,
        "to_id": 102,
        "intimacy_level_min": 30,
        "intimacy_level_max": 70,
        "have_conversation": True,
    }
    response = make_api_request_sync("GET", "/intimacy/", params=intimacy_params)
    print(json.dumps(response, indent=4))


def test_intimacy_store():
    print("Testing Intimacy Store...")
    store_intimacy_data = {"from_id": 101, "to_id": 104, "intimacy_level": 50}
    response = make_api_request_sync("POST", "/intimacy/", data=store_intimacy_data)
    print(json.dumps(response, indent=4))


def test_intimacy_update():
    print("Testing Intimacy Update...")
    update_intimacy_data = {"from_id": 101, "to_id": 104, "new_intimacy_level": 55}
    response = make_api_request_sync("PUT", "/intimacy/", data=update_intimacy_data)
    print(json.dumps(response, indent=4))


def test_intimacy_decrease_all():
    print("Testing Intimacy Decrease All...")
    response = make_api_request_sync("PATCH", "/intimacy/decrease_all", data={})
    print(json.dumps(response, indent=4))


def test_encounter_count_store():
    print("Testing Encounter Count Store...")
    store_encounter_count_data = {"from_id": 101, "to_id": 103, "count": 1}
    response = make_api_request_sync(
        "POST", "/encounter_count/", data=store_encounter_count_data
    )
    print(json.dumps(response, indent=4))


def test_encounter_count_get():
    print("Testing Encounter Count Get...")
    # Ensure encounter count exists before getting
    store_encounter_count_data = {"from_id": 101, "to_id": 102, "count": 2}
    make_api_request_sync("POST", "/encounter_count/", data=store_encounter_count_data)

    encounter_count_params = {"from_id": 101, "to_id": 102}
    response = make_api_request_sync(
        "GET", "/encounter_count/", params=encounter_count_params
    )
    print(json.dumps(response, indent=4))


def test_encounter_count_by_from_id():
    print("Testing Encounter Count by From ID...")
    # # Ensure encounter counts exist before getting
    # store_encounter_count_data = {"from_id": 101, "to_id": 102, "count": 10}
    # make_api_request_sync("POST", "/encounter_count/", data=store_encounter_count_data)
    # time.sleep(1)
    # store_encounter_count_data = {"from_id": 101, "to_id": 107, "count": 5}
    # make_api_request_sync("POST", "/encounter_count/", data=store_encounter_count_data)
    # time.sleep(1)
    # store_encounter_count_data = {"from_id": 101, "to_id": 100, "count": 100}
    # make_api_request_sync("POST", "/encounter_count/", data=store_encounter_count_data)
    # time.sleep(1)

    encounter_by_from_id_params = {"from_id": 101, "k": 5}
    response = make_api_request_sync(
        "GET", "/encounter_count/by_from_id", params=encounter_by_from_id_params
    )
    print(json.dumps(response, indent=4))


def test_encounter_count_increment():
    print("Testing Encounter Count Increment...")
    increment_encounter_count_data = {"from_id": 101, "to_id": 103}
    response = make_api_request_sync(
        "PUT",
        "/encounter_count/increment",
        data=increment_encounter_count_data,
    )
    print(json.dumps(response, indent=4))


def test_encounter_count_update():
    print("Testing Encounter Count Update...")
    update_encounter_count_data = {"from_id": 101, "to_id": 102, "count": 5}
    response = make_api_request_sync(
        "PUT", "/encounter_count/", data=update_encounter_count_data
    )
    print(json.dumps(response, indent=4))


def test_cv_store():
    print("Testing CV Store...")
    # Ensure all required fields are provided
    store_cv_data = {
        "jobid": 201,
        "characterId": 101,
        "CV_content": "Experienced warrior with leadership skills.",
        "week": 12,
        "health": 80,
        "studyxp": 5,
        "date": 20240115,
        "jobName": "Knight",
        "election_status": "not_yet",
    }
    response = make_api_request_sync("POST", "/cv/", data=store_cv_data)
    print(json.dumps(response, indent=4))


def test_cv_update_election_status():
    print("Testing CV Update Election Result...")
    # Ensure CV exists before updating election result
    # Insert CV if it does not exist
    store_cv_data = {
        "jobid": 203,
        "characterId": 102,
        "CV_content": "Skilled archer with tactical expertise.",
        "week": 13,
        "health": 90,
        "studyxp": 6,
        "date": 20240116,
        "jobName": "Archer",
        "election_status": "not_yet",
    }
    make_api_request_sync("POST", "/cv/", data=store_cv_data)

    update_election_status_data = {
        "characterId": 102,
        "election_status": "succeeded",
        "jobid": 203,
        "week": 13,
    }
    response = make_api_request_sync(
        "PUT", "/cv/election_status", data=update_election_status_data
    )
    print(json.dumps(response, indent=4))


def test_cv_get():
    print("Testing CV Get...")
    # Ensure CV exists before getting
    get_cv_params = {
        "jobid": 203,
        "characterId": 102,
        "week": 13,
        "election_status": "succeeded",
    }
    response = make_api_request_sync("GET", "/cv/", params=get_cv_params)
    print(json.dumps(response, indent=4))


def test_actions_store():
    print("Testing Actions Store...")
    store_action_data = {
        "characterId": 101,
        "action": "Patrol",
        "result": {"success": True, "area_patrolled": "North Gate"},
        "description": "Patrolled the North Gate successfully.",
    }
    response = make_api_request_sync("POST", "/actions/", data=store_action_data)
    print(json.dumps(response, indent=4))


def test_actions_get():
    print("Testing Actions Get...")
    get_action_params = {"characterId": 101, "action": "Patrol", "k": 2}
    response = make_api_request_sync("GET", "/actions/", params=get_action_params)
    print(json.dumps(response, indent=4))


def test_descriptors_store():
    print("Testing Descriptors Store...")
    store_descriptor_data = {
        "failed_action": "Failed Patrol",
        "action_id": 301,
        "characterId": 101,
        "reflection": "Need to improve vigilance during patrols.",
    }
    response = make_api_request_sync(
        "POST", "/descriptors/", data=store_descriptor_data
    )
    print(json.dumps(response, indent=4))


def test_descriptors_get():
    print("Testing Descriptors Get...")
    # Ensure descriptor exists before getting
    get_descriptor_params = {"action_id": 301, "characterId": 101, "k": 1}
    response = make_api_request_sync(
        "GET", "/descriptors/", params=get_descriptor_params
    )
    print(json.dumps(response, indent=4))


def test_daily_objectives_store():
    print("Testing Daily Objectives Store...")
    store_daily_objective_data = {
        "characterId": 101,
        "objectives": ["Train archery", "Scout the perimeter"],
    }
    response = make_api_request_sync(
        "POST", "/daily_objectives/", data=store_daily_objective_data
    )
    print(json.dumps(response, indent=4))


def test_daily_objectives_get():
    print("Testing Daily Objectives Get...")
    get_daily_objectives_params = {"characterId": 101, "k": 2}
    response = make_api_request_sync(
        "GET", "/daily_objectives/", params=get_daily_objectives_params
    )
    print(json.dumps(response, indent=4))


def test_plans_store():
    print("Testing Plans Store...")
    store_plan_data = {
        "characterId": 101,
        "detailed_plan": "Increase training hours and participate in strategy meetings.",
    }
    response = make_api_request_sync("POST", "/plans/", data=store_plan_data)
    print(json.dumps(response, indent=4))


def test_plans_get():
    print("Testing Plans Get...")
    get_plans_params = {"characterId": 101, "k": 1}
    response = make_api_request_sync("GET", "/plans/", params=get_plans_params)
    print(json.dumps(response, indent=4))


def test_meta_sequences_store():
    print("Testing Meta Sequences Store...")
    store_meta_seq_data = {
        "characterId": 102,
        "meta_sequence": ["scout_area()", "gather_resources()", "set_up_camp()"],
    }
    response = make_api_request_sync(
        "POST", "/meta_sequences/", data=store_meta_seq_data
    )
    print(json.dumps(response, indent=4))


def test_meta_sequences_get():
    print("Testing Meta Sequences Get...")
    get_meta_sequences_params = {"characterId": 102, "k": 1}
    response = make_api_request_sync(
        "GET", "/meta_sequences/", params=get_meta_sequences_params
    )
    print(json.dumps(response, indent=4))


def test_meta_sequences_update():
    print("Testing Meta Sequences Update...")
    update_meta_seq_data = {
        "characterId": 102,
        "meta_sequence": ["Assess situation", "Develop strategy", "Implement actions"],
    }
    response = make_api_request_sync(
        "PUT", "/meta_sequences/", data=update_meta_seq_data
    )
    print(json.dumps(response, indent=4))


def test_diaries_store():
    print("Testing Diaries Store...")
    store_diary_data = {
        "characterId": 101,
        "diary_content": "Today I trained with the archers and improved my aim.",
    }
    response = make_api_request_sync("POST", "/diaries/", data=store_diary_data)
    print(json.dumps(response, indent=4))


def test_diaries_get():
    print("Testing Diaries Get...")
    get_diaries_params = {"characterId": 101, "k": 3}
    response = make_api_request_sync("GET", "/diaries/", params=get_diaries_params)
    print(json.dumps(response, indent=4))


def test_characters_store():
    print("Testing Characters Store...")
    character_data = {
        "characterId": 102,
        "characterName": "Diana",
        "gender": "Female",
        "spriteId": 0,
        "relationship": "Scout",
        "personality": "Swift and silent",
        "long_term_goal": "Protect the realm with unparalleled archery skills",
        "short_term_goal": "Scout the area for potential threats",
        "language_style": "Stealthy and precise",
        "biography": "An agile ranger with unparalleled archery skills.",
    }
    response = make_api_request_sync("POST", "/characters/", data=character_data)
    print(json.dumps(response, indent=4))


def test_characters_get():
    print("Testing Characters Get...")
    get_character_params = {"characterId": 102}
    response = make_api_request_sync("GET", "/characters/", params=get_character_params)
    print(json.dumps(response, indent=4))


def test_characters_rag():
    print("Testing Characters RAG...")
    get_character_rag_params = {"characterId": 102, "topic": "Archery", "k": 2}
    response = make_api_request_sync(
        "GET", "/characters/rag", params=get_character_rag_params
    )
    print(json.dumps(response, indent=4))


def test_characters_rag_in_list():
    print("Testing Characters RAG in List...")

    get_character_rag_in_list_params = {
        "characterId": 102,
        "topic": "Leadership",
        "characterList": [1, 2, 3],  # 直接传递列表，而不是 JSON 字符串
        "k": 3,
    }
    response = make_api_request_sync(
        "POST", "/characters/rag_in_list", data=get_character_rag_in_list_params
    )
    print(json.dumps(response, indent=4))


def test_characters_update():
    print("Testing Characters Update...")
    update_character_data = {
        "characterId": 102,
        "update_fields": {
            "personality": "Swift, silent, and observant",
            "short_term_goal": "Map the unexplored forests",
        },
    }
    response = make_api_request_sync("PUT", "/characters/", data=update_character_data)
    print(json.dumps(response, indent=4))


def test_knowledge_store():
    print("Testing Knowledge Store...")
    store_knowledge_data = {
        "characterId": 101,
        "day": 10,
        "environment_information": "The northern forests are dense and full of wildlife.",
        "personal_information": "Prefers early morning training sessions.",
    }
    response = make_api_request_sync("POST", "/knowledge/", data=store_knowledge_data)
    print(json.dumps(response, indent=4))


def test_knowledge_get():
    print("Testing Knowledge Get...")
    get_knowledge_params = {"characterId": 101, "day": 10}
    response = make_api_request_sync("GET", "/knowledge/", params=get_knowledge_params)
    print(json.dumps(response, indent=4))


def test_knowledge_get_latest():
    print("Testing Knowledge Get Latest...")
    get_latest_knowledge_params = {"characterId": 101, "k": 2}
    response = make_api_request_sync(
        "GET", "/knowledge/latest", params=get_latest_knowledge_params
    )
    print(json.dumps(response, indent=4))


def test_knowledge_update():
    print("Testing Knowledge Update...")
    update_knowledge_data = {
        "characterId": 101,
        "day": 10,
        "environment_information": "The northern forests have new threats emerging.",
        "personal_information": "Considering changing training routines.",
    }
    response = make_api_request_sync("PUT", "/knowledge/", data=update_knowledge_data)
    print(json.dumps(response, indent=4))


def test_character_arc_store():
    print("Testing Character Arc Store...")
    store_character_arc_data = {
        "characterId": 101,
        "category": [
            {"item": "skill", "origin_value": "beginner"},
            {"item": "emotion", "origin_value": "neutral"},
        ],
    }
    response = make_api_request_sync(
        "POST", "/character_arc/", data=store_character_arc_data
    )
    print(json.dumps(response, indent=4))


def test_character_arc_get():
    print("Testing Character Arc Get...")
    get_character_arc_params = {"characterId": 101}
    response = make_api_request_sync(
        "GET", "/character_arc/", params=get_character_arc_params
    )
    print(json.dumps(response, indent=4))


def test_character_arc_with_changes():
    print("Testing Character Arc with Changes...")
    get_character_arc_with_changes_params = {"characterId": 101, "k": 2}
    response = make_api_request_sync(
        "GET",
        "/character_arc/with_changes",
        params=get_character_arc_with_changes_params,
    )
    print(json.dumps(response, indent=4))


def test_character_arc_update():
    print("Testing Character Arc Update...")
    update_character_arc_data = {
        "characterId": 101,
        "category": [
            {"item": "skill", "origin_value": "intermediate"},
            {"item": "emotion", "origin_value": "happy"},
        ],
    }
    response = make_api_request_sync(
        "PUT", "/character_arc/", data=update_character_arc_data
    )
    print(json.dumps(response, indent=4))


def test_character_arc_change_store():
    print("Testing Character Arc Change Store...")
    store_character_arc_change_data = {
        "characterId": 101,
        "item": "Leadership",
        "cause": "Saved the village from invaders.",
        "context": "During the winter festival.",
        "change": "Became the leader of the village guard.",
    }
    response = make_api_request_sync(
        "POST", "/character_arc/change", data=store_character_arc_change_data
    )
    print(json.dumps(response, indent=4))


def test_character_arc_changes_get():
    print("Testing Character Arc Changes Get...")
    get_character_arc_changes_params = {
        "characterId": 101,
        "item": "Leadership",
        "k": 1,
    }
    response = make_api_request_sync(
        "GET", "/character_arc/changes", params=get_character_arc_changes_params
    )
    print(json.dumps(response, indent=4))


def test_sample_get_all():
    print("Testing Sample Get All...")
    response = make_api_request_sync("GET", "/sample/", params={})
    print(json.dumps(response, indent=4))


def test_sample_get_specific():
    print("Testing Sample Get Specific...")
    sample_params = {"item_name": "personality"}
    response = make_api_request_sync("GET", "/sample/", params=sample_params)
    print(json.dumps(response, indent=4))


def test_agent_prompt_store():
    print("Testing Agent Prompt Store...")
    # Ensure that agent prompt does not already exist to avoid duplicate error
    # Delete if exists
    delete_agent_prompt_data = {"characterId": 101}
    try:
        make_api_request_sync("DELETE", "/agent_prompt/", data=delete_agent_prompt_data)
    except Exception:
        pass  # If it doesn't exist, ignore

    store_agent_prompt_data = {
        "characterId": 101,
        "daily_goal": "sleep well",
        "refer_to_previous": True,
        "life_style": "Busy",
        "daily_objective_ar": "",
        "task_priority": [],
        "max_actions": 10,
        "meta_seq_ar": "",
        "replan_time_limit": 1,
        "meta_seq_adjuster_ar": "",
        "focus_topic": [],
        "depth_of_reflection": "Deep",
        "reflection_ar": "",
        "level_of_detail": "Shallow",
        "tone_and_style": "Gentle",
    }
    response = make_api_request_sync(
        "POST", "/agent_prompt/", data=store_agent_prompt_data
    )
    print(json.dumps(response, indent=4))


def test_agent_prompt_get():
    print("Testing Agent Prompt Get...")
    get_agent_prompt_params = {"characterId": 101}
    response = make_api_request_sync(
        "GET", "/agent_prompt/", params=get_agent_prompt_params
    )
    print(json.dumps(response, indent=4))


def test_agent_prompt_update():
    print("Testing Agent Prompt Update...")
    update_agent_prompt_data = {
        "characterId": 101,
        "update_fields": {
            "daily_goal": "Enhance perimeter security.",
            "max_actions": 6,
        },
    }
    response = make_api_request_sync(
        "PUT", "/agent_prompt/", data=update_agent_prompt_data
    )
    print(json.dumps(response, indent=4))


def test_agent_prompt_delete():
    print("Testing Agent Prompt Delete...")
    delete_agent_prompt_data = {"characterId": 101}
    response = make_api_request_sync(
        "DELETE", "/agent_prompt/", data=delete_agent_prompt_data
    )
    print(json.dumps(response, indent=4))


def test_conversation_prompt_store():
    print("Testing Conversation Prompt Store...")
    # Ensure that conversation prompt does not already exist to avoid duplicate error
    # Delete if exists
    delete_conversation_prompt_data = {"characterId": 101}
    try:
        make_api_request_sync(
            "DELETE", "/conversation_prompt/", data=delete_conversation_prompt_data
        )
    except Exception:
        pass  # If it doesn't exist, ignore

    store_conversation_prompt_data = {
        "characterId": 101,
        "topic_requirements": "Randomly criticize others dressing.",
        "relation": "Always treat others as enemy.",
        "emotion": "You are angry.",
        "personality": "Introversion",
        "habits_and_preferences": "Running everyday.",
    }
    response = make_api_request_sync(
        "POST", "/conversation_prompt/", data=store_conversation_prompt_data
    )
    print(json.dumps(response, indent=4))


def test_conversation_prompt_get():
    print("Testing Conversation Prompt Get...")
    get_conversation_prompt_params = {"characterId": 101}
    response = make_api_request_sync(
        "GET", "/conversation_prompt/", params=get_conversation_prompt_params
    )
    print(json.dumps(response, indent=4))


def test_conversation_prompt_update():
    print("Testing Conversation Prompt Update...")
    update_conversation_prompt_data = {
        "characterId": 101,
        "update_fields": {
            "emotion": "Calm",
            "habits_and_preferences": "Prefers detailed discussions.",
        },
    }
    response = make_api_request_sync(
        "PUT", "/conversation_prompt/", data=update_conversation_prompt_data
    )
    print(json.dumps(response, indent=4))


def test_conversation_prompt_delete():
    print("Testing Conversation Prompt Delete...")
    delete_conversation_prompt_data = {"characterId": 101}
    response = make_api_request_sync(
        "DELETE", "/conversation_prompt/", data=delete_conversation_prompt_data
    )
    print(json.dumps(response, indent=4))


def test_decision_store():
    print("Testing Decision Store...")
    # 第一条决策数据
    store_decision_data_1 = {
        "characterId": 101,
        "need_replan": True,
        "action_description": [
            "Going to mine to gather resources",
            "Selling ore at the market for profit",
            "Heading to school for education upgrade",
            "Taking a rest at home to recover energy",
        ],
        "action_result": [
            "Action 'goto mine' succeeded: Successfully reached the mine at 10:30",
            "Action 'gomining 2' succeeded: Obtained 20 ore, energy decreased by 20",
            "Action 'sell ore 15' failed: Not in the market location",
            "Action 'goto market' succeeded: Arrived at market, ready for trading",
        ],
        "new_plan": [
            "goto market -> sell ore 15 -> goto school",
            "goto mine -> gomining 3 -> goto home",
            "goto school -> study 2 -> goto home",
        ],
        "daily_objective": [
            "Earn 200 coins through mining and trading",
            "Upgrade education level to college",
            "Maintain health above 80%",
            "Build relationships at the square",
        ],
        "meta_seq": [
            "goto mine; gomining 2; goto market; sell ore 30; goto school; study 2",
            "goto home; sleep 6; goto mine; gomining 3; goto market; sell ore 40",
            "goto square; socialize 2; goto mine; gomining 2; goto market",
        ],
        "reflection": [
            "Day 1 Review: Successfully mined 20 ore and earned 150 coins. Failed one market transaction due to location error. Need to check location before transactions.",
            "Day 2 Review: Reached education milestone and built new relationships. Market prices were lower than expected. Should check prices before selling.",
            "Day 3 Review: Maintained good health but spent too much time traveling. Need to optimize route planning and group activities by location.",
        ],
    }

    response_1 = make_api_request_sync("POST", "/decision/", data=store_decision_data_1)
    print("Store Decision Response 1:")
    print(json.dumps(response_1, indent=4))

    time.sleep(1)  # 确保有时间戳差异

    # 第二条决策数据（与第一条相同角色ID，但稍作修改）
    store_decision_data_2 = {
        "characterId": 101,
        "need_replan": False,
        "action_description": [
            "Going to school for advanced study",
            "Heading to market to buy tools",
        ],
        "action_result": [
            "Action 'goto school' succeeded: Reached school at 9:00",
            "Action 'study 2' succeeded: Gained 10 knowledge points",
        ],
        "new_plan": ["goto school -> study 2 -> goto home"],
        "daily_objective": [
            "Upgrade education level to university",
            "Earn 300 coins through trading",
        ],
        "meta_seq": ["goto school; study 2; goto market; buy tools; goto home"],
        "reflection": [
            "Day 4 Review: Improved educational status and purchased necessary tools. Next step is to increase earnings.",
            "Day 5 Review: balabalabala",
        ],
    }

    response_2 = make_api_request_sync("POST", "/decision/", data=store_decision_data_2)
    print("Store Decision Response 2:")
    print(json.dumps(response_2, indent=4))


def test_decision_get():
    print("Testing Decision Get...")
    # 假设需要合并结果并取最新的5条内容（如果不需要合并，就不传count）
    # get_decision_params = {"characterId": 101, "count": 4}
    get_decision_params = {"characterId": 101}
    response = make_api_request_sync("GET", "/decision/", params=get_decision_params)
    print(json.dumps(response, indent=4))


def test_current_pointer_store():
    print("Testing Current Pointer Store...")
    store_current_pointer_data = {"characterId": 101, "current_pointer": "pointer_1"}
    response = make_api_request_sync(
        "POST", "/current_pointer/", data=store_current_pointer_data
    )
    print(json.dumps(response, indent=4))


def test_current_pointer_get():
    print("Testing Current Pointer Get...")
    get_current_pointer_params = {"characterId": 101}
    response = make_api_request_sync(
        "GET",
        f"/current_pointer/{get_current_pointer_params['characterId']}",
        params={},
    )
    print(json.dumps(response, indent=4))


def test_current_pointer_update():
    print("Testing Current Pointer Update...")
    update_current_pointer_data = {"characterId": 101, "current_pointer": "pointer_2"}
    response = make_api_request_sync(
        "PUT", "/current_pointer/", data=update_current_pointer_data
    )
    print(json.dumps(response, indent=4))


def test_current_pointer_delete():
    print("Testing Current Pointer Delete...")
    delete_current_pointer_params = {"characterId": 101}
    response = make_api_request_sync(
        "DELETE",
        f"/current_pointer/{delete_current_pointer_params['characterId']}",
        params={},
    )
    print(json.dumps(response, indent=4))


def test_conversation_store():
    print("Testing Conversation Store...")
    store_conversation_data = {
        "from_id": 1,
        "to_id": 2,
        "start_time": "10:00",
        "start_day": 1,
        "message": "Hello! How are you?",
        "send_gametime": [1, "10:02"],
        "send_realtime": "2024-12-16 20:00",
    }
    response = make_api_request_sync(
        "POST", "/conversation/", data=store_conversation_data
    )
    print(json.dumps(response, indent=4))


# def test_conversation_store():
#     print("Testing Conversation Store...")
#     conversations = [
#         {
#             "from_id": 1,
#             "to_id": 2,
#             "start_time": "10:00",
#             "start_day": 1,
#             "message": "Hello! How are you?",
#             "send_gametime": [1, "10:02"],
#             "send_realtime": "2024-12-16 20:00",
#         },
#         {
#             "from_id": 1,
#             "to_id": 2,
#             "start_time": "11:00",
#             "start_day": 1,
#             "message": "Are you coming to the meeting?",
#             "send_gametime": [1, "11:05"],
#             "send_realtime": "2024-12-16 21:00",
#         },
#         {
#             "from_id": 2,
#             "to_id": 1,
#             "start_time": "12:00",
#             "start_day": 1,
#             "message": "Yes, I'll be there.",
#             "send_gametime": [1, "12:10"],
#             "send_realtime": "2024-12-16 22:00",
#         },
#         {
#             "from_id": 1,
#             "to_id": 3,
#             "start_time": "13:00",
#             "start_day": 2,
#             "message": "Did you finish the report?",
#             "send_gametime": [2, "13:15"],
#             "send_realtime": "2024-12-17 09:00",
#         },
#     ]

#     for conversation in conversations:
#         response = make_api_request_sync("POST", "/conversation/", data=conversation)
#         print(json.dumps(response, indent=4))
#         time.sleep(0.5)  # 确保每条记录有不同的时间戳


def test_conversation_get():
    print("Testing Conversation Get...")
    get_conversation_params = {"from_id": 1, "to_id": 2, "k": 5}
    response = make_api_request_sync(
        "GET", "/conversation/", params=get_conversation_params
    )
    print(json.dumps(response, indent=4))

    # Test with start_day and start_time
    get_conversation_params = {
        "from_id": 1,
        "to_id": 2,
        "start_day": 1,
        "start_time": "10:00",
    }
    response = make_api_request_sync(
        "GET", "/conversation/", params=get_conversation_params
    )
    print(json.dumps(response, indent=4))

    # Test with characterId and start_day
    get_conversation_params = {"characterId": 1, "start_day": 1}
    response = make_api_request_sync(
        "GET", "/conversation/", params=get_conversation_params
    )
    print(json.dumps(response, indent=4))


def test_conversation_memory_store():
    print("Testing Conversation Memory Store...")
    store_conversation_memory_data = {
        "characterId": 101,
        "day": 1,
        "topic_plan": ["Discuss strategy", "Review patrol routes"],
        "time_list": ["09:00", "14:00"],
        "started": [{"time": "09:00", "topic": "Discuss strategy"}],
    }
    response = make_api_request_sync(
        "POST", "/conversation_memory/", data=store_conversation_memory_data
    )
    print(json.dumps(response, indent=4))


def test_conversation_memory_get():
    print("Testing Conversation Memory Get...")
    get_conversation_memory_params = {"characterId": 101, "day": 1}
    response = make_api_request_sync(
        "GET", "/conversation_memory/", params=get_conversation_memory_params
    )
    print(json.dumps(response, indent=4))


def test_conversation_memory_update():
    print("Testing Conversation Memory Update...")
    update_conversation_memory_data = {
        "characterId": 101,
        "day": 1,
        "update_fields": {"topic_plan": ["Discuss new strategy"]},
    }
    response = make_api_request_sync(
        "PUT", "/conversation_memory/", data=update_conversation_memory_data
    )
    print(json.dumps(response, indent=4))


def test_conversation_memory_add_started():
    print("Testing Conversation Memory Add Started...")
    add_started_data = {
        "characterId": 101,
        "day": 1,
        "add_started": {"time": "14:00", "topic": "Review patrol routes"},
    }
    response = make_api_request_sync(
        "PUT", "/conversation_memory/", data=add_started_data
    )
    print(json.dumps(response, indent=4))


def test_work_experience_store():
    print("Testing Work Experience Store...")
    store_work_experience_data = {
        "characterId": 101,
        "jobid": 1,
        "start_date": 20230101,
    }
    response = make_api_request_sync(
        "POST", "/work_experience/", data=store_work_experience_data
    )
    print(json.dumps(response, indent=4))


def test_work_experience_get_all():
    print("Testing Work Experience Get All...")
    get_all_work_experiences_params = {"characterId": 101}
    response = make_api_request_sync(
        "GET", "/work_experience/all", params=get_all_work_experiences_params
    )
    print(json.dumps(response, indent=4))


def test_work_experience_get_current():
    print("Testing Work Experience Get Current...")
    get_current_work_experience_params = {"characterId": 101}
    response = make_api_request_sync(
        "GET", "/work_experience/current", params=get_current_work_experience_params
    )
    print(json.dumps(response, indent=4))


def test_work_experience_update():
    print("Testing Work Experience Update...")
    update_work_experience_data = {
        "characterId": 101,
        "jobid": 1,
        "additional_work": 10,
        "additional_salary": 500.0,
    }
    response = make_api_request_sync(
        "PUT", "/work_experience/", data=update_work_experience_data
    )
    print(json.dumps(response, indent=4))


def test_get_memory_api():
    print("Testing Get Memory API...")
    get_memory_params = {"characterId": 1, "day": 1, "count": 5}
    response = make_api_request_sync(
        "GET", "/conversation_memory/memory", params=get_memory_params
    )
    print(json.dumps(response, indent=4))


def main():

    test_get_memory_api()

    # # Test work experience endpoints
    # test_work_experience_store()
    # time.sleep(1)
    # test_work_experience_get_all()
    # time.sleep(1)
    # test_work_experience_get_current()
    # time.sleep(1)
    # test_work_experience_update()
    # time.sleep(1)
    # test_work_experience_get_all()

    # # Test conversation memory endpoints
    # test_conversation_memory_store()
    # time.sleep(1)
    # test_conversation_memory_get()
    # time.sleep(1)
    # test_conversation_memory_update()
    # time.sleep(1)
    # test_conversation_memory_add_started()
    # time.sleep(1)
    # test_conversation_memory_get()  # Verify updates

    # # Test conversation endpoints
    # test_conversation_store()
    # time.sleep(1)
    # test_conversation_get()
    # time.sleep(1)

    # # 测试 current_pointer 的增删查改
    # test_current_pointer_store()
    # time.sleep(1)
    # test_current_pointer_get()
    # time.sleep(1)
    # test_current_pointer_update()
    # time.sleep(1)
    # test_current_pointer_get()  # 验证更新
    # time.sleep(1)
    # test_current_pointer_delete()
    # time.sleep(1)
    # test_current_pointer_get()  # 验证删除

    # test_decision_store()
    # time.sleep(1)  # 等待数据写入
    # test_decision_get()

    # # CRUD Operations
    # test_crud_insert()
    # time.sleep(1)  # Adding delay to ensure data is inserted before update
    # test_crud_update()
    # time.sleep(1)
    # test_crud_find()
    # time.sleep(1)
    # test_crud_delete()
    # time.sleep(1)

    # # # Vector Search
    # # test_vector_search()
    # # time.sleep(1)

    # # Impressions
    # test_impressions_get()
    # time.sleep(1)
    # test_impressions_store()
    # time.sleep(1)

    # # Intimacy
    # test_intimacy_get()
    # time.sleep(1)
    # test_intimacy_store()
    # time.sleep(1)
    # test_intimacy_update()
    # time.sleep(1)
    # test_intimacy_decrease_all()
    # time.sleep(1)

    # # Encounter Count
    # test_encounter_count_store()
    # time.sleep(1)
    # test_encounter_count_get()
    # time.sleep(1)
    # test_encounter_count_by_from_id()
    # time.sleep(1)
    # test_encounter_count_increment()
    # time.sleep(1)
    # test_encounter_count_update()
    # time.sleep(1)

    # # CV
    # test_cv_store()
    # time.sleep(1)
    # test_cv_update_election_status()
    # time.sleep(1)
    # test_cv_get()
    # time.sleep(1)

    # # Actions
    # test_actions_store()
    # time.sleep(1)
    # test_actions_get()
    # time.sleep(1)

    # # Descriptors
    # test_descriptors_store()
    # time.sleep(1)
    # test_descriptors_get()
    # time.sleep(1)

    # # Daily Objectives
    # test_daily_objectives_store()
    # time.sleep(1)
    # test_daily_objectives_get()
    # time.sleep(1)

    # # Plans
    # test_plans_store()
    # time.sleep(1)
    # test_plans_get()
    # time.sleep(1)

    # # Meta Sequences
    # test_meta_sequences_store()
    # time.sleep(1)
    # test_meta_sequences_get()
    # time.sleep(1)
    # test_meta_sequences_update()
    # time.sleep(1)

    # # Diaries
    # test_diaries_store()
    # time.sleep(1)
    # test_diaries_get()
    # time.sleep(1)

    # # Characters
    # test_characters_store()
    # time.sleep(1)
    # test_characters_get()
    # time.sleep(1)
    # test_characters_rag()
    # time.sleep(1)
    # test_characters_rag_in_list()
    # time.sleep(1)
    # test_characters_update()
    # time.sleep(1)

    # # Knowledge
    # test_knowledge_store()
    # time.sleep(1)
    # test_knowledge_get()
    # time.sleep(1)
    # test_knowledge_get_latest()
    # time.sleep(1)
    # test_knowledge_update()
    # time.sleep(1)

    # # Character Arc
    # test_character_arc_store()
    # time.sleep(1)
    # test_character_arc_get()
    # time.sleep(1)
    # test_character_arc_with_changes()
    # time.sleep(1)
    # test_character_arc_update()
    # time.sleep(1)
    # test_character_arc_change_store()
    # time.sleep(1)
    # test_character_arc_changes_get()
    # time.sleep(1)

    # # Sample
    # test_sample_get_all()
    # time.sleep(1)
    # test_sample_get_specific()
    # time.sleep(1)

    # # Agent Prompt
    # test_agent_prompt_store()
    # time.sleep(1)
    # test_agent_prompt_get()
    # time.sleep(1)
    # test_agent_prompt_update()
    # time.sleep(1)
    # test_agent_prompt_delete()
    # time.sleep(1)

    # # Conversation Prompt
    # test_conversation_prompt_store()
    # time.sleep(1)
    # test_conversation_prompt_get()
    # time.sleep(1)
    # test_conversation_prompt_update()
    # time.sleep(1)
    # test_conversation_prompt_delete()
    # time.sleep(1)


if __name__ == "__main__":
    main()
