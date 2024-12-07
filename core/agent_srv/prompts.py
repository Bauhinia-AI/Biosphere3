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


            The final format should be a list of daily objectives. Like this:\n
            ["Working: Working in the farm","Studying: Discover something about science", "Socializing: Try to make friends"]\n
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
    Current Location: {current_location}

    Please analyze the error and provide an alternative approach considering:
    1. If the error is location-related, ensure proper navigation
    2. If the error is timing-related, adjust the sequence timing
    3. If the error is resource-related, add necessary resource gathering steps
    4. If the error is prerequisite-related, add missing prerequisite actions
    {% endif %}

    Current sequence:
    {meta_seq}

    Please provide a revised action sequence that:
    1. Avoids the failed action or its problematic conditions
    2. Still achieves the original objectives where possible
    3. Includes any necessary preparatory steps
    4. Takes into account the current location and context
    """
)

reflection_prompt = ChatPromptTemplate.from_template(
    """As an AI agent, please analyze your recent activities and generate a thoughtful reflection.

    Recent Objectives:
    {past_objectives}

    Errors and Replanning History:
    {replan_history}

    Character Current State:
    {character_stats}

    Please provide:
    1. A comprehensive reflection on your activities
    2. Analysis of patterns in errors and mistakes
    3. What worked well and what didn't
    4. Specific lessons learned
    5. Suggestions for future improvement

    Focus on:
    - Patterns in failed actions and their root causes
    - Effectiveness of replanning strategies
    - Progress towards objectives
    - Resource management and timing
    - Location-based challenges
    - Interaction patterns with the environment
    """
)

describe_action_result_prompt = ChatPromptTemplate.from_template(
    """Based on the following action result,
    provide a brief description for the action result, like: I successfully studied for 2 hours.
    {action_result}
    """
)
