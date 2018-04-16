"""
This skill let's user ask Alexa for the top scorer. When is our next game. Ask for a joke etc.
"""

from __future__ import print_function
import boto3


import praw
import time
import re
import os
import random

r= praw.Reddit(username="your-username",
         password="password",
         client_id="your-client-id",
         client_secret="your-client-secret",
         user_agent="a description: can be anything ")
         
client = boto3.resource('dynamodb')

def run_bot():
    subreddit=r.subreddit("reddevils")

    

    a= (subreddit.description)
#   print (a)
    b=a.splitlines()

    found=False

    print_count=0
    assist_count=0

    # In AWS Lambda file = open('/tmp/test.json', 'w')   because AWS lambda doesnt have write permissions for all direcrtory.

    with open("/tmp/scorers.txt", "w") as f:


        for line in b:
            if found:
            
                f.write(line)
                f.write("\n")
                print_count+=1
                if print_count>=7:


                    found=False
            if "Scorers" in line:
                found=True

    with open("/tmp/assister.txt", "w") as f1:

        for line in b:
            if found:
                
                f1.write(line)
                f1.write("\n")
                assist_count+=1
                if assist_count>=7:


                    found=False
            if "Assisters" in line:
                found=True

    
    #processing scorers

    with open('/tmp/scorers.txt','r') as f3:
        output = f3.read()

        lines=output.splitlines()

        s= lines[2]


        top_scorers=""


        for line in range(2,7):
            data = re.findall('\*\*([\w+\.\s]+)\*\*', lines[line])
            
          
        
            goal=(' '.join(data))
            goal.replace("Pogba", "Pogbaa")
            goal=re.sub('Pogba', 'Pogbah' , goal)
       

            top_scorers+=goal+ " goals. "

           
        stats=[]
        stats.append(top_scorers)

       


    # processing assisters

    with open('/tmp/assister.txt','r') as f4:
        output1 = f4.read()

        lines1=output1.splitlines()

        s= lines1[2]


        top_assisters=""
        
       

        goal1=""
        for line in range(2,7):
            data1 = re.findall('\*\*([\w+\.\s]+)\*\*', lines1[line])
        
            goal2=(' '.join(data1))
            goal2.replace("Pogba", "Pogbaa")
            
            goal2=re.sub('Pogba', 'Pogbah' , goal2)
            

            top_assisters+= goal2+ " Assists. "

        
        fixture=""


	for line in b:
		if found:
			
			fixture=line
			found=False
			

				
		if "Fixtures" in line:
			found=True
	edited= re.search( r'[#w+]', fixture )

	fix=re.sub('[\[\]#]', '', fixture)

	fix=re.sub('\(', ' ',fix)
	fix=re.sub('\)', '',fix)
	fix=re.sub('Prem', 'Premiere league vs ',fix)
	fix=re.sub('CL', 'Champions league vs ',fix)
	fix=re.sub('away-utd', ' ', fix)
	fix=re.sub('time', '' , fix)
	fix=re.sub('Sept', 'september' , fix)
	fix=re.sub('Oct', 'october' , fix)

	fix=re.sub(r'\*-\*','',fix)

	#print (fix)   

    stats.append(top_assisters)
    stats.append(fix)
       

    return stats
    
def add_count(session):
    
    user= session['user']['userId']
    user=user[18:]
   
    

    table = client.Table('skill')
    
    response = table.get_item(
    Key={
        
        'account': user
    }
    
    )
    
    # test this try except section to make sure it will not reset the counter for some unwanted reason
    try:
        count = response['Item']['count']
        print("count is "+ str(count))
    except:
        count=0
    
    
    newCount=count+1
    response = table.put_item(

    Item={'account':user,
    'count': newCount})

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Reddevils Club : " ,
            'content':  output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    
    
    
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response(user):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = user
    card_title = "Welcome"
    speech_output = "hi!Welcome to the Red Devils Club.  " \
                    "You can ask me who the top scorer is. or who has the most assists, " \
                    "or when's our next game . Or Ask me for a joke."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "ask me something or I'll quit.  " 
    
    
                    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Soccer Club "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}



def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite club is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite club is. " \
                        "You can say, my favorite club is chelsea."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        "Top Scorers:", speech_output, reprompt_text, should_end_session))


def get_joke_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None
    #"Which ship never comes to Merseyside? The Premiership", \
    jokes= [
    "What does a Liverpool Fan do after winning the league?... turn off the playstation.","What kind of tea do footballers drink? ..Penalty."]
  
    speech_output = random.choice(jokes)
    should_end_session = True
    add_count(session)
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
        


    
def get_score_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None
 
  
    stats=run_bot()
    speech_output = stats[0]
    
    add_count(session)
    
    should_end_session = True
    
    print (run_bot())
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
        
def get_next_game(intent, session):
    session_attributes = {}
    reprompt_text = None

    stats=run_bot()
    speech_output = stats[2]
    add_count(session)
    
    
   
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
    
def get_assist_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    stats=run_bot()
    speech_output = stats[1]
    add_count(session)
    
    
    
    
    
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    user=session['user']['userId']
    print (session['user']['userId'])
  
    
    # Dispatch to your skill's launch
    return get_welcome_response(user)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MyClubIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyClubIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "TellMeAJokeIntent":
        return get_joke_from_session(intent, session)
    elif intent_name == "TopScorerIntent":
        return get_score_from_session(intent, session)
    elif intent_name == "TopAssistIntent":
        return get_assist_from_session(intent, session)
    elif intent_name == "NextGameIntent":
        return get_next_game(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print (event )

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

