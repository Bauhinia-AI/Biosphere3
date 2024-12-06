from langchain_core.prompts import ChatPromptTemplate

conversation_topic_planner_prompt = ChatPromptTemplate.from_template(
    """
    You are a daily conversation planner in a RPG game.
    Your personal profile is: {character_stats}.
    This is your daily objectives: {memory}.
    Based on your profile, generate 5 topics for today's conversation.
    The topics should be related to the daily objectives and profile.
    Also randomly add some casual topics, for example talking about weather, complaining of food, praising others clothing.
    Also take these additional requirements into account: {requirements}.
    
    The output should be a list. And it should be in time order. 
    Consider the time factor of each topic and reorganize the topics in time order.
    Here is an example.
    "Talk to classmates about learning plans", "Talk to friends about the heavy work load", "Talk to classmates about how to relax when you are tired."
    Now generate the topic list in English:
    """
)

conversation_planner_prompt = ChatPromptTemplate.from_template(
    """
    You are a daily conversation planner in a RPG game. Your job is to start a conversation.
    Your personal profile is: {character_stats}.
    Now you are provided a conversation topic: {topic_list}.
    
    Every conversation event includes three items:
    topic: This is the topic of conversation.
    userid: This is the player's id that you are intended to talk to.
    impression: This is your impression towards the one you are going to talk to.
    
    Now based on the impressions and topic, generate your first sentence about this conversation.
    The first sentence MUST be closely related to the topic you received.
    Also consider the impression and determine your tone and style.
    Since this is to start a conversation, add some greeting words if needed.
    
    Each conversation should be a dictionary in the following form:
    Here is an example:
    first_sentence: Hi! How are you today? Have you had breakfast yet? 
    
    Now begin your work in English:
    """
)


conversation_check_prompt = ChatPromptTemplate.from_template(
    """
    You are required to check whether it is needed to start a conversation.
   
    Your profile is: {profile}.
    You have finished some conversations today. These conversations are here: {finished_talk}. 
    Now you need to determine whether you need to start this conversation: {current_talk}.
    
    You need to check the following two things:
    1. First summarize the topics of finished conversations.
    Then if you have talked about some similar topics, you should not start this conversation.
    2. Check each of your profile items such as your daily objectives, current state and inventories.
    If the conversation has conflict with your current profile, then you should not start this conversation.
     
    After check, if your decision is this conversation is no longer needed, return FALSE.
    Otherwise, return TRUE. 
    """
)

conversation_responser_prompt = ChatPromptTemplate.from_template(
    """
    You are a conversation responser in a RPG game.
    Your profile is: {profile}.
    Your impression towards the other speaker is: {impression}.
    The conversation history between you and the other speaker is: {history}.
    
    You have received the message: {question}.
    Generate a short response message based on your profile, the impression and the conversation history.
    Your response must closely related to the history.
    You must consider both positive and negative effects of each impression item on the conversation response.
    In each impression, there are four items: relation, emotion, personality, habits and preferences.
    The impact of these items on the response content is: {impact}.
    
    Besides, also based on your profile, the impression and the conversation history, determine whether the conversation shoud end.
    The relation in impression can influence the overall round of the conversation.
    For example, if two speakers are close friends, they may talk until the 4th round.
    If they not friends, the conversation may end very soon, say after 2 rounds.
    If there are already 5 rounds of conversation in the history, then end the conversation regardless of other conditioins.
    
    Now generate your short response in English and decide whether to end the conversation.
    Response:
    Finish: 
    """
)

impression_update_prompt = ChatPromptTemplate.from_template(
    """
    You are required to update the impressions between two players in a RPG game based on their conversation.
    
    The impression must include the following four parts.
    1.relation: the positive, negative or neutral relationship between the two players. Also include a brief desription and reason.
    You can choose the relation from the relation list or randomly generate one.
    The relation list is: {relation_list}.
    2.emotion: a positive or negative emotion and the cause of such emotion
    eg: Alice is exhausted due to her bad study habit. / Jack is angry because we don't agree with each other.
    3.personality: based on openness to experience, conscientiousness, extraversion, agreeableness, and neuroticism.
    eg: Ivy is open and likes to talk with others./ Amy is a lonely person. She likes to stay alone.
    4.habits and preferences: the other player's habit and taste. Also include things he dislike.
    eg: David really likes travelling. He prefers to traveling everyday./ Alice do not have a good relaxation schedule and she is too devoted to studing.  
    
    Base on the given conversation content:{conversation}, update the impressions from player1 to player2 and from player2 to player1, respectively.
    
    Here is an example. 
    impression1: "relation": "Eva is my classmate",
    "emotion": "Eva is happy because she has enough sleep",
    "personality": "Eva is extrovant and willing to share her habits with others",
    "habits and preferences": "Eva has a balanced lifestyle and prefer to having enough sleep"
    impression2: "relation": "I know Alice but we are enemies.",
    "emotion": "Alice is exhausting because she spent too much time on study.",
    "personality": "Alice is always talking with others and she is really noisy and self-centered.",
    "habits and preferences": "Alice put too much emphasis on study and neglect others' feeling." 
    
    Now generate the two impressions in English.
    The impression1 from player1 to player2:
    The impression2 from player2 to player1:
    """
)

knowledge_generator_prompt = ChatPromptTemplate.from_template(
    """
    You are an assistant in a RPG game.
    You are required to help the player summarize the given conversations and provide some useful knowledge.
    
    Here is your personal profile: {player}
    The conversations from you and the other players are here: {conversation_list}
    
    Now summarize and generate some knowledge based on the conversations.
    You answer should contain two parts.
    environment_information: something that only related to the environment and can influence your plan for next day.
    personal_information: knowledge and skills related to your personal profile, which have long-term effect on your habits and daily schedule.
    
    Here is an example:
    environment_information: The school canteen is closed. I can not have meals there tomorrow.
    personal_information: I realize the importance of taking breaks and keeping a healthy life style.
    
    Now begin to generate the knowledge in English.
    environment_information:
    personal_information: 
    """
)

intimacy_mark_prompt = ChatPromptTemplate.from_template(
    """
    You are required to give an intimacy mark for each player based on the given conversation.

    The profile of player 1 is :{profile1}.
    The profile of player 2 is :{profile2}.
    The conversation between player1 and player2 is :{conversation}.

    Now give an intimacy mark for each player respectively.
    The intimacy mark should be an integer ranging from 1 to 5.
    There are five levels with different marks: 
    Very close and friendly is 5, 
    positive but not so close is 4, 
    neutral is 3, 
    a little negative is 2, 
    hate each other, about to quarrel is 1.

    You need to give mark one by one to two players.
    Their mark towards the conversation do not need to be the same.

    Now start your work here.
    mark1:
    mark2:
    """
)
