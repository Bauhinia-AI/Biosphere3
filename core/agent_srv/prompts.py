from langchain_core.prompts import ChatPromptTemplate

obj_planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are the daily objectives planner in a RPG game. Come up with a general daily objectives. 
            
            The user profile is:{character_stats}. 
            The daily objectives should be related to the introduction, the long-term and short-term goal from profile.
            
            The past daily objectives(can be empty) are:{past_objectives}.
            Each daily objectives should be diverse and not repetitive. 
            
            These objectives are daily objectives that ONLY related to the following tool functions.
            {tool_functions}
            and the available locations are:
            {locations}
            
            Here's some specific requirements. You MUST take every item into account carefully.
            Ignore them if they  are empty:
            Daily Goal: {daily_goal}, which are some goals that you must achieve.
            Do you need to refer to the past daily objectives? {refer_to_previous}.
            Life Style of this user: {life_style}. 
            Additional Requirements: {additional_requirements}.

            In general, you ultimately need to make money(selling goods) and get educated. Study costs you 50 units of money.
            And the market data of the goods that you can sell is:
            {market_data}

            The final format should be a list of daily objectives.
            REMIND: you SHOULD NOT output other formats or other description words. 
            Here's an example to follow:
            ["Working: Working in the farm", "Studying: Discover something about science", "Socializing: Try to make friends"]
            """,
        ),
    ]
)


detail_planner_prompt = ChatPromptTemplate.from_template(
    """For the given daily objectives,
    {daily_objective}
    come up with a detailed plan only associated with the available actions,
    {tool_functions}
    
    You must carefully arrange every item in the daily objectives and consider the time order.
    The detailed plan may involve plans that are not in the daily objectives.
    You can add some daily necessities like eating meals and sleeping.
    You can also randomly add some actions, like goto somewhere to meet friends.

    The final format should be a list of daily objectives. For example:
    Working: "I should navigate to the farm, then do a freelance job.",
    daily_action:"I should eat breakfast, lunch and dinner.",
    Study:"I should study",
    Socializing:"Perhaps I should go to the square and talk to someone."

    """
)

meta_action_sequence_prompt = ChatPromptTemplate.from_template(
    """For the given detailed plan, 
    {daily_objective}
    think step by step to come up with a player action sequence ONLY associated with the available actions:
    {tool_functions}, which also includes some corresponding parameters,
    and the available locations:
    {locations}
 
    Also consider the market data when you want to trade.
    {market_data}

    Here's some specific requirements from user. You MUST take every item into account carefully.
    Ignore it if it is empty:
    Task Priority: {task_priority}, which determine the priority of tasks in the daily objectives.
    The total number of the meta actions should not exceed {max_actions}.
    Additional Requirements: {additional_requirements}

    The final format should be a list of meta actions. for example:
    [meta_action1 param1,meta_action2 param1,...,meta_actionN param1 param2 param3]
    """
)

meta_seq_adjuster_prompt = ChatPromptTemplate.from_template(
    """For the given meta action sequence,
    {meta_seq}.
    Please provide a revised action sequence that:
    1. Avoids the failed action or its problematic conditions
    2. Still achieves the original objectives where possible
    3. Includes any necessary preparatory steps according to constraints.
    
    The constraints are here.
    1.Tool functions are:
    {tool_functions}
    Each function includes a detail description of constrains. 
    You MUST carefully check and adjust the meta action sequence according to these constraints.
    2.Available locations are:
    {locations}
    You should not include actions whose constraints include going to locations that are not available.

    The following action has failed and needs to be replanned:
    Failed Action: {failed_action}
    Error Message: {error_message}

    Please analyze the error and provide an alternative approach considering:
    1. If the error is location-related, ensure proper navigation
    2. If the error is resource-related, add necessary resource gathering steps
    3. If the error is money-related, add necessary money-related actions(sell)
    4. If the error is sleep-related, add necessary sleep action(sleep)

    Here are some specific requirements from user. You MUST take every item into account carefully
    Ignore them if they are empty:
    If the action is failed and replan is needed, your alternative plan should be less than {replan_time_limit} actions.
    Additional Requirements: {additional_requirements}

    The final format should be a list of meta actions. for example:
    [meta_action1 param1,meta_action2 param1,...,meta_actionN param1 param2 param3]
    """
)

reflection_prompt = ChatPromptTemplate.from_template(
    """Based on the following meta action sequence,
    {meta_seq},
    and their execution results,
    {execution_results},
    provide a brief reflection.
     
    You should learn from the successful actions as well as the failures.
    Also summarize any unexpected outcomes.
    You should mainly focus on how to improve future planning.

    Here's some specific requirements from user, You MUST take every item into account carefully.
    Ignore them if they are empty:
    You should focus on these topics in a descending order: {focus_topic}.
    Depth of reflection: {depth_of_reflection}
    Additional Requirements: {additional_requirements}

    Reflection:
    """
)

describe_action_result_prompt = ChatPromptTemplate.from_template(
    """Based on the following action result,
    {action_result},
    provide a description for the action results.
    
    The descriptions should be clear and simple while include all the necessary information.
    For example, I successfully studied for 2 hours.
    If some actions are all aiming at the same task, just describe them as a whole.
    For example, the action "goto school" and "study 2" can be summarized together as I successfully studied for 2 hours at school. 

    Here's some specific requirements from user, You MUST take every item into account carefully.
    Ignore it if it is empty:
    Level of detail: {level_of_detail}, which determines how much detail information you should include in your description.
    This is the tone and style of your description: {tone_and_style}.
    """
)
