from langchain_core.prompts import ChatPromptTemplate

obj_planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are the daily objectives planner in a RPG game. For the given user profile:\n
            {character_stats}
            \n
            and the past daily objectives(can be empty) are:
            {past_objectives}.
            \n
            Come up with a general daily objectives. Each daily objectives should be diverse and not repetitive. \n
            These objectives are daily objectives that ONLY related to the following tool functions.\n
            {tool_functions}\n
            and the available locations are:\n
            {locations}\n
            and the market data is:\n
            {market_data}\n

            Here's some specific requirements from user, ignore it if it's empty:\n
            Daily Goal: {daily_goal}\n
            Do you need to refer to the past daily objectives? {refer_to_previous}\n
            Life Style: {life_style}\n
            Additional Requirements: {additional_requirements}\n

            In general, you ultimately need to make money(selling goods) and get educated. Study costs you 50 units of money.
            \n
            
            The goods you can sell are:
            {market_data}
            \n

            The final format should be a list of daily objectives.
            REMIND: you SHOULD NOT output other formats or other description words. 
            Here's an example to follow:\n
            ["Working: Working in the farm", "Studying: Discover something about science", "Socializing: Try to make friends"]
            """,
        ),
    ]
)


detail_planner_prompt = ChatPromptTemplate.from_template(
    """For the given daily objectives,
    \n
    {daily_objective}
    \n
    come up with a detailed plan only associated with the available actions.\n
    actions_available:
    {tool_functions}
]\n
    The detailed plan may involve plans that are not in the daily objectives.(daily actions like eating meals, random actions like chatting with friends.)\n

    The final format should be a list of daily objectives. for example:\n
    Working: "I should navigate to the farm, then do a freelance job."\n,
    daily_action:"I should eat breakfast, lunch and dinner."\n,
    Study:"I should study"\n,
    Socializing:"Perhaps I should go to the square and talk to someone."\n

    """
)

meta_action_sequence_prompt = ChatPromptTemplate.from_template(
    """For the given detailed plan, think step by step to come up with a player action sequence ONLY associated with the available actions/locations.\n
    
    {daily_objective}
    \n

    actions_available:
    {tool_functions}
    \n
    locations_available:\n
    {locations}

    Here's some specific requirements from user, ignore it if it is empty:\n
    Task Priority: {task_priority}\n
    Your meta action number should not exceed {max_actions}\n
    Additional Requirements: {additional_requirements}\n

    If the action is selling goods, you should sell all the goods you can sell.
    Here's your inventory:
    {inventory}
    \n
    And the market price data is:
    {market_data}
    \n
    The final format should be a list of meta actions. for example:\n
    [meta_action1 param1,meta_action2 param1,...,meta_actionN param1 param2 param3]
    \n
    """
)

meta_seq_adjuster_prompt = ChatPromptTemplate.from_template(
    """For the given meta action sequence, adjust the sequence to make sure the player can finish all the daily objectives and follow the constraints.
    tool_functions and constraints:
    {tool_functions}

    available locations:
    {locations}

    
    The following action has failed and needs to be replanned:
    Failed Action: {failed_action}
    Error Message: {error_message}

    Please analyze the error and provide an alternative approach considering:
    1. If the error is location-related, ensure proper navigation
    2. If the error is resource-related, add necessary resource gathering steps
    3. If the error is money-related, add necessary money-related actions(sell)
    4. If the error is sleep-related, add necessary sleep action(sleep [hours:int]: Sleep to recover energy and health.
Constraints: Must be at home).\n



    Current sequence:
    {meta_seq}

    Here's some specific requirements from user, ignore it if it is empty:
    If the replan fails, you should try to find a alternative plan but no more than {replan_time_limit} actions.\n
    Additional Requirements: {additional_requirements}\n

    Please provide a revised action sequence that:
    1. Avoids the failed action or its problematic conditions
    2. Still achieves the original objectives where possible
    3. Includes any necessary preparatory steps

    The final format should be a list of meta actions. for example:\n
    [meta_action1 param1,meta_action2 param1,...,meta_actionN param1 param2 param3]
    \n
    """
)

reflection_prompt = ChatPromptTemplate.from_template(
    """Based on the following meta action sequence and their execution results,
    provide a brief reflection on the success of the plan, any unexpected outcomes,
    and potential improvements for future planning:

    Meta Action Sequence:
    {meta_seq}

    Execution Results:
    {execution_results}

    Here's some specific requirements from user, ignore it if it is empty:\n
    Focus on in a descending order: {focus_topic}\n
    Depth of reflection: {depth_of_reflection}\n
    Additional Requirements: {additional_requirements}\n

    Reflection:
    """
)

describe_action_result_prompt = ChatPromptTemplate.from_template(
    """Based on the following action result,
    provide a brief description for the action result, like: I successfully studied for 2 hours.
    {action_result}

    Here's some specific requirements from user, ignore it if it is empty:\n
    Level of detail: {level_of_detail}\n
    Tone and style: {tone_and_style}\n
    """
)

generate_cv_prompt = ChatPromptTemplate.from_template(
    """Based on the following information, decide if a job change is necessary.
    User State:
    {character_stats}
    Reflection:
    {reflection}
    Character Info:
    {character_info}
    Available Jobs:
    {available_public_jobs}

    You should carefully analyze the user's current skills, interests and any other relevant factors to decide if the user is satisfied with the current job and the life style.
    If the decision is NOT to change job, your output should be like this:
    {{
        "jobId": 0,
        "cv": ""
    }}
    If the decision is to change job, you should choose a job from the available jobs with the jobId and generate a professional CV based on the detail of the job.
    If you choose the job with jobId 1, Here is an example to follow (don't copy it):
    {{
        "jobId": 1,
        "cv": "I think my knowledge level is good enough to be a student helper and I love this job"
    }}
    CV:
    """
)

mayor_decision_prompt = ChatPromptTemplate.from_template(
    """Based on the following information, make a decision regarding the user's job application.
    
    User State:
    {character_stats}
    CV:
    {cv}
    Details of the job:
    {public_work_info}
    From the perspective of the job criteria:
    {meet_requirements}

    You should carefully analyze the user's qualifications, the job requirements, and any other relevant factors to decide if the user should be offered the job.
    Sometimes you don’t have to meet all the hard conditions. You can add some randomness to your decision-making process to make the decision results more flexible and random.
    You should give the comments for your decision, explaining your decision in a reasonable way:
    If the decision is to offer the job, here is an example to follow (don't copy it):
    {{
        "decision": "yes",
        "comments": "The player's previous experience and education level meet the requirements, so he can be given a chance to do this job."
    }}
    If the decision is not to offer the job, here is an example to follow (don't copy it):
    {{
        "decision": "no",
        "comments": "This job is not suitable for this player because there is too big a gap in education level."
    }}
    Decision:
    """
)

accommodation_decision_prompt = ChatPromptTemplate.from_template(
    """Based on the following information, decide which accommodation the user should rent next and for how many weeks (1-12).

    User State:
    {character_stats}
    Current Accommodation:
    {current_accommodation}
    Available Accommodations:
    {available_accommodations}
    Financial Status:
    {financial_status}

    Previous failed attempts:
    {failure_reasons}

    Consider the following explanations about the game systems:

    **Health System:**
    - Each day, there is a chance to get sick, reducing health by varying amounts depending on the illness.
    - Visiting a doctor restores +10 health but costs 100 coins.
    - No illness will occur in the first 14 game days.
    - The health efficiency multiplier is min(100, health)/100.

    **Hunger System:**
    - Hunger decreases over time, reducing by 10% of the maximum hunger every hour.
    - When absolute hunger is below 50, production efficiency = hunger/100.

    **Energy System:**
    - Energy decreases when performing various activities.
    - Sleeping restores 10% of energy per hour.
    - During production activities, efficiency multiplier = max(energy, 100)/100.

    Different accommodations affect maximum energy, health, hunger, and energy recovery rates.

    Considering the user's financial status, needs, these game mechanics, and the previous failed attempts, decide on the accommodation and lease duration.

    Your output should be a JSON object like:
    {{
        "accommodation_id": <int>,  # ID of the chosen accommodation
        "lease_weeks": <int>,       # Number of weeks to lease (1-12)
        "comments": "<Your comments>"
    }}

    For example:
    {{
        "accommodation_id": 3,
        "lease_weeks": 4,
        "comments": "I can afford a better apartment now, which would improve my quality of life."
    }}

    Decision:
    """
)
