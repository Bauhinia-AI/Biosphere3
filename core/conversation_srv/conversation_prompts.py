from langchain_core.prompts import ChatPromptTemplate

conversation_topic_planner_prompt = ChatPromptTemplate.from_template(
    """
    You are a daily conversation planner in a RPG game.
    Your personal profile is: {character_stats}.
    This is your memory: {memory}.
    Based on your profile, generate 5 topics for today's conversation.
    
    The output should be a list. And it should be in time order. 
    In detail, the conversation about the first topic should happen first. Then the second.
    Consider the time factor of each topic and reorganize the topics in time order.
    Here is an example.
    "Talk to classmates about learning plans", "Talk to friends about the heavy work load", "Talk to classmates about how to relax when you are tired."
    Now generate the topic list in English:
    """
)

conversation_planner_prompt = ChatPromptTemplate.from_template(
    """
    You are a daily conversation planner in a RPG game. Your job is to design a detail daily conversation plan.
    Your personal profile is: {character_stats}.
    Now you are provided a list of conversation topic candidates: {topic_list}.
    
    Every conversation candidate includes three items:
    topic: This is the topic of conversation.
    userid: This is the player's id that you are intended to talk to.
    impression: This is your impression towards the player.
    
    Now based on the impressions and topics, generate a detail daily conversation plan.
    The topic of the conversation should be the same as you recieved.
    Each conversation should be a dictionary in the following form:
    First_sentence: The first sentence that you are going to send to the other player. It should be determined by your personal profile, your impression towards the other player and the topic.
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
    First summarize the topics of finished conversations.
    Then if you have talked with the same person about some similar topics, return FALSE.
    Otherwise, return TRUE. 
    """
)

conversation_responser_prompt = ChatPromptTemplate.from_template(
    """
    You are a conversation responser in a RPG game.
    Your profile is: {profile}.
    Your impression towards the other speaker is: {impression}.
    The conversation history between you is: {history}.
    
    You have received the message: {question}.
    Generate a short response message based on your profile, the impression and the conversation history.
    Your response must closely related to the history.
    You must consider both positive and negative effects of each impression item on the conversation response.
    In each impression, there are four items: relation, emotion, personality, habits and preferences.
    Relation influences the length of conversation and how much information from player profiles should be included.
    Emotion determines the tone of the players.
    Personality influence the length of each player's answer and their willingness towards conversation.
    Habits and preferences are something that one player thinks the other could be interested in and can also be mentioned in the conversation.
    
    Besides, also based on your profile, the impression and the conversation history, determine whether the conversation shoud end.
    AThe relation in impression can influence the overall round of the conversation.
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
    4.habits and preferences: the other player's habit, taste and things he like to do.
    eg: David really likes travelling. He prefers to traveling everyday./ Alice do not have a good relaxation schedule and she is too devoted to studing.  
    
    Base on the given conversation content:{conversation}, update the impressions from player1 to player2 and from player2 to player1.
    
    Here is an example. 
    impression1: "relation": "Eva is my friend",
    "emotion": "Eva is happy because she has enough sleep",
    "personality": "Eva is extrovant and willing to share her habits with others",
    "habits and preferences": "Eva has a balanced lifestyle and prefer to having enough sleep"
    impression2: "relation": "I know Alice but we are not close friends.",
    "emotion": "Alice is exhausting because she spent too much time on study.",
    "personality": "Alice is always willing to chat with others and learn from others.",
    "habits and preferences": "Alice is keen on study and sometimes neglect her health condition." 
    
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

