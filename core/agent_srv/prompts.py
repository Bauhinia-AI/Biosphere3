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

            Here's some specific requirements from user, ignore it if it's empty:\n
            Daily Goal: {daily_goal}\n
            Do you need to refer to the past daily objectives? {refer_to_previous}\n
            Life Style: {life_style}\n
            Additional Requirements: {additional_requirements}\n

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
    4. If the error is sleep-related, add necessary sleep action(sleep)



    Current sequence:
    {meta_seq}

    Here's some specific requirements from user, ignore it if it is empty:
    If the replan fails, you should try to find a alternative plan but no more than {replan_time_limits} actions.\n
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
