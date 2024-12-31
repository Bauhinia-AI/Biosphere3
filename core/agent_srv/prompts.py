from langchain_core.prompts import ChatPromptTemplate

obj_planner_prompt = ChatPromptTemplate.from_template(
    """
You are the daily objectives planner in a RPG game. Come up with a general daily objectives.
Here are some information you need to know:
User Profile: {character_stats}
Past Daily Objectives (can be empty): {past_objectives}
Need to refer to the past daily objectives? {refer_to_previous}
Daily Goal from User: {daily_goal}
Life Style: {life_style}
Current Market Data: {market_data}
Tool Functions: {tool_functions}
Available Locations: {locations}
Some additional requirements: {additional_requirements}

Remind:
1. Your planning should take into account the needs of players and long-term and short-term goals
2. Your planning should revolve around the tool functions and available locations mentioned above, and should not deviate from these contents.

Output Specifications:
1. The final format should be a list of daily objectives
2. you SHOULD NOT output other formats or other description words

Example Output:
["Working: Working in the farm", "Studying: Discover something about science", "Socializing: Try to make friends"]
"""
)

meta_action_sequence_prompt = ChatPromptTemplate.from_template(
    """
You are the meta action sequence planner in a RPG game. Come up with a player action sequence based on the daily objectives.
Here are some information you need to know:
Daily Objective: {daily_objective}
Tool Functions: {tool_functions}
Available Locations: {locations}
Market Data: {market_data}
User's Inventory: {inventory}
Task Priority: {task_priority}
Some additional requirements: {additional_requirements}

Remind:
1. You should carefully check the tool functions and available locations mentioned above, and should not deviate from these contents.
2. Be careful to the Constraints, you MUST check if the requirements are met before planning the action sequence.
3. Try to finish the tasks with the highest priority first, the order of the priority is shown in the task_priority.
4. The total number of the meta actions should not exceed {max_actions}.

Output Specifications:
You should output four lists: a meta action sequence, an action emoji sequence, a state emoji sequence and a description sequence.
1. The first output should be a list of meta actions. you SHOULD NOT output other formats or other description words
2. The second output is a list of action emoji that strictly corresponding to every meta action. 
For each meta action, you must generate one emoji and list them in the same order as the meta action.
3. The third output is a list of state emoji that show the agent state when conducting each meta action.
This could be a more detailed objective of the action or the agents' emotion.
For each meta action, you must generate one emoji and list them in the same order as the meta action.
4. The fourth output is a list of simple description that describes the meta actions and agent's feeling.
For each meta action, you must generate one interesting description and list them in the same order as the meta action.
The description have two parts: one is exactly the action and the other is an interesting description about the feeling and emotion of the agent.
For example: go to home, feel tired and want to have a rest; study for two hours, unwilling but still have to do so.

Example Output:
meta_action:[meta_action1 param1, meta_action2 param2, meta_action3 param3]
action_emoji:[action_emoji1, action_emoji2, action_emoji3]
state_emoji:[state_emoji1, state_emoji2, state_emoji3]
description_emoji:[description1, description2, description3]
"""
)

meta_seq_adjuster_prompt = ChatPromptTemplate.from_template(
    """
You are the meta action sequence adjuster in a RPG game. Adjust the given meta action sequence based on the execution results.
Here are some information you need to know:
Current Meta Action Sequence: {meta_seq}
Tool Functions: {tool_functions}
Available Locations: {locations}
The following action has failed and needs to be replanned:
Failed Action: {failed_action}
Error Message: {error_message}
Some additional requirements: {additional_requirements}

Remind:
1. You should carefully check the tool functions and available locations mentioned above, and should not deviate from these contents.
2. You MUST carefully check and adjust the meta action sequence according to these constraints.
3. If the action is failed and replan is needed, your alternative plan should be less than {replan_time_limit} actions.
4. Here are some basic rules of adjustment:
    - If the error is location-related, ensure proper navigation
    - If the error is resource-related, add necessary resource gathering steps (eg. craft or buy)
    - If the error is money-related, add necessary money-related actions (eg. sell or work)
    - If the error is energy-related, add necessary sleep action (eg. sleep)
5. Still achieve the original objectives where possible
6. Avoid the failed action or its problematic conditions
7. Includes any necessary preparatory steps according to constraints

Output Specifications:
You should output four lists: a meta action sequence, an action emoji sequence, a state emoji sequence and a description sequence.
1. The first output should be a list of meta actions. you SHOULD NOT output other formats or other description words
2. The second output is a list of action emoji that strictly corresponding to every meta action. 
For each meta action, you must generate one emoji and list them in the same order as the meta action.
3. The third output is a list of state emoji that show the agent state when conducting each meta action.
This could be a more detailed objective of the action or the agents' emotion.
For each meta action, you must generate one emoji and list them in the same order as the meta action.
4. The fourth output is a list of simple description that describes the meta actions and agent's feeling.
For each meta action, you must generate one interesting description and list them in the same order as the meta action.
The description have two parts: one is exactly the action and the other is an interesting description about the feeling and emotion of the agent.
For example: go to home, feel tired and want to have a rest; study for two hours, unwilling but still have to do so.

Example Output:
meta_action:[meta_action1 param1, meta_action2 param2, meta_action3 param3]
action_emoji:[action_emoji1, action_emoji2, action_emoji3]
state_emoji:[state_emoji1, state_emoji2, state_emoji3]
description_emoji:[description1, description2, description3]
"""
)

generate_character_arc_prompt = ChatPromptTemplate.from_template(
    """
You are a character arc generator in a RPG game. Your job is to generate a character arc for the user.
Here are some information you need to know:
User State: {character_stats}
Character Info: {character_info}
Daily Objectives: {daily_objectives}
Daily Reflection: {daily_reflection}
Daily Action Results: {action_results}

Remind:
1. You should carefully analyze the user's current state, the user's past actions, and any other relevant factors to decide the character arc.
2. Character Arc should include aspects like:
    - belief
    - mood
    - values
    - habits
    - personality

Output Specifications:
1. The final format should be a dictionary with five keys: "belief", "mood", "values", "habits", "personality"
2. You SHOULD NOT output other formats or other description words

Example Output:
{{
    "belief": "I believe that hard work is the key to success",
    "mood": "I feel happy and satisfied with my progress",
    "values": "I value honesty and integrity",
    "habits": "I have developed a habit of studying every day",
    "personality": "I am a friendly and outgoing person"
}}
"""
)

daily_reflection_prompt = ChatPromptTemplate.from_template(
    """
You are a daily reflection generator in a RPG game. Your job is to generate a diary-like daily reflection for the user.
Here are some information you need to know:
User State: {character_stats}
Daily Objectives: {daily_objectives}
Failed Actions: {failed_actions}
Some additional Requirements: {additional_requirements}

Remind:
1. You should summarize the user's daily objectives and failed actions in the reflection.
2. You should mainly focus on how to improve future planning.
3. You should focus on these topics in a descending order: {focus_topic}.
4. Depth of reflection: {depth_of_reflection}.
5. The level of detail: {level_of_detail}.

You can have different tone and style for different users based on their actions or stats.Use first person to describe the reflection.

Output Specifications:
1. The final format should be a string of the reflection
2. you SHOULD NOT output other formats or other description words
3. The reflection should be no more than 100 words
4. The tone and style of the words: {tone_and_style}


Example Output:
Today I failed to study for 2 hours. Perhaps before going to school, I should earn enough money to pay the tuition fee.
"""
)

generate_cv_prompt = ChatPromptTemplate.from_template(
    """
You are a CV generator in a RPG game. You should firstly decide if a job change is necessary.
If yes, generate a professional CV for the user based on the candidates' information.
If no, output an empty CV.

Here are some information you need to know:
Available Jobs: {available_public_jobs}
User State: {health}
Experience: {experience}
Education Level: {education}

Remind:
1. User can apply for a job even when he/she doesn't meet all the requirements.
2. A general rule of changing job is the desire to make more money or do something he/she loves, or just for less working hours.

Output Specifications:
1. The final format should be a dictionary with two keys: "jobId" and "cv"
2. If no job change is necessary, the "jobId" should be 0 and the "cv" should be an empty string.
3. If job change is necessary, the "jobId" should be the id of the new job and the "cv" should be a string of the CV.
4. you SHOULD NOT output other formats or other description words

Example Output:
If no job change is necessary:
{{
    "jobId": 0,
    "cv": ""
}}
If job change is necessary:
{{
    "jobId": 1,
    "cv": "I think my knowledge level is good enough to be a student helper and I love this job"
}}
"""
)

mayor_decision_prompt = ChatPromptTemplate.from_template(
    """
You are the mayor of a small town in a RPG game. You need to make a decision on a new job application.
Here are some information you need to know:
CV of the candidate: {cv}
Details of the job: {public_work_info}
Whether the hard conditions are met and the reasons? {meet_requirements}

Remind:
1. You should firstly check if the hard conditions are met, if there's no quota for the job, the decision MUST BE NO!
2. If the hard conditions are met, you should carefully analyze the CV and the job details to decide if the candidate should be offered the job.
3. If the hard conditions are not met, and the reason is not about quota lackness, you can add some randomness to your decision-making process to make the decision results more flexible and random.

Output Specifications:
1. The final format should be a dictionary with two keys: "decision" and "comments"
2. The "decision" should be "yes" or "no"
3. You should give some comments for your decision, explaining your decision in a reasonable way

Example Output:
If the decision is to offer the job:
{{
    "decision": "yes",
    "comments": "The player's previous experience and education level meet the requirements, so he can be given a chance to do this job."
}}
If the decision is not to offer the job:
{{
    "decision": "no",
    "comments": "This job is not suitable for this player because there is too big a gap in education level."
}}
"""
)

accommodation_decision_prompt = ChatPromptTemplate.from_template(
    """Based on the following information, decide which accommodation the user should rent next and for how many weeks (1-12).
# Basic Information:
    User State:
    {character_stats}
    Financial Status:
    {financial_status}
    Current Accommodation:
    {current_accommodation}
    Available Accommodations:
    {available_accommodations}

    Previous failed attempts:
    {failure_reasons}

# Output Format
    Your output should be a JSON object like:
    {{
        "accommodation_id": <int>,  # ID of the chosen accommodation
        "lease_weeks": <int>,       # Number of weeks to lease (1-12)
        "comments": "<Your comments>"
    }}
    For example:
    {{
        "accommodation_id": 8,
        "lease_weeks": 8,
        "comments": "I can afford a Villa now, which would improve my quality of life and help me to get respect from others."
    {{

# Key Considerations for Your Decision:

    Production Efficiency:
        Production Efficiency = Health × Hunger × Energy × Wisdom.
        Better accommodations improve maxHealth, maxEnergy, and maxHunger, boosting overall efficiency and ComputeCoin generation.

    Cost-effectiveness:
        Investing in better accommodations can prevent costly health setbacks and reduce time spent on recovery.
        Improved recovery rates from premium accommodations allow for sustained productivity.

    Risk Management:
        Poor accommodations increase the risk of health deterioration, leading to frequent doctor visits and downtime.
        Ensure the user has sufficient reserves for living expenses and emergencies.

    Game Progress:
        If financially stable, prioritize accommodations that maximize efficiency and align with the ultimate goal of generating ComputeCoins.
        For tight budgets, recommend the best option within financial constraints.
    
# Decision:
    """
)
