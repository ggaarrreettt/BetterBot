from datetime import date
import datetime
import requests
import json
from math import ceil
from colorama import init
init(autoreset=True)
from colorama import Fore, Back, Style
from BetterBot import BetterBot

BASE_URL = "https://api.groupme.com/v3"

ACCESS_TOKEN = ""

TEST_TOKEN = ""

NEW_TOKEN = ""


GROUP_ID = ""

MSGS_PER_PAGE = 20

PROJECT_NAME = "BetterBot"


def getChats():
    sesh = requests.session()

    endpoint = 'https://v2.groupme.com/groups/' + GROUP_ID + '/messages'

    headers = {
        'Accept': 'application/json, text/javascript',
        'Accept-Charset': 'ISO-8859-1,utf-8',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/json',
        'Origin': 'https://web.groupme.com',
        'Referer': 'https://web.groupme.com/groups/' + GROUP_ID,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
        'X-Access-Token': ACCESS_TOKEN
    }

    params = {'before_id': ''}

    r = sesh.get(endpoint, params=params, headers=headers)

    # with open("FormattedTest.text", 'w') as tempFile:

    (msg) = json.loads(r.text)

    # Total number of msgs
    total_msg = msg.get('response').get('count')

    # Number of times we need to iterate
    total_iterations = ceil((total_msg / MSGS_PER_PAGE))

    print("Total Iterations == {}".format(total_iterations))

    userin = int(input("Continue? (0 to stop)"))
    if userin == 0:
        exit(-1)

    params = {}
    # Now iterate through all the msgs
    for i in range(total_iterations):
        time = datetime.datetime.now()



        print("{}<{}>".format(Fore.RED, time))
        r = sesh.get(endpoint, params=params, headers=headers)
        msg = json.loads(r.text)

        last_id = msg.get('response').get('messages')[-1].get('id')

        params = {'before_id': last_id}

        for text in msg.get('response').get('messages'):
            print(text.get('text'))

def getInput():
    time = datetime.datetime.now()
    userInput = str(input(Fore.RED + "<{}>: ".format(time)))
    userInput = userInput.split(' ', 1)
    return userInput

def displayHelp():
    print(f"{Fore.GREEN}Help Menu:")
    print(f"{Fore.BLUE}'say'")

if __name__ == '__main__':
    print("{}Welcome to {}! {}'stop' to quit the program".format(Fore.GREEN, PROJECT_NAME, Fore.RED))

    myBot = BetterBot("EMAIL", "PASSWORD")

    # Prime the while loop
    userInput = getInput()

    # Parse through user input
    while (userInput[0].lower() != 'stop'):

        # SAY command
        if (userInput[0].lower() == 'say' and len(userInput) == 2):  # say something in the chat
            myBot.say(userInput[1], GROUP_ID)

        # SAVE command
        elif (userInput[0].lower() == 'save'):
            if len(userInput) == 2:
                myBot.save_messages(GROUP_ID, userInput[1])
            else:
                myBot.save_messages(GROUP_ID)

        elif (userInput[0].lower() == 'due'):
            myBot.display_dues(GROUP_ID)

        elif (userInput[0].lower() == 'adddue'):
            if len(userInput) == 2:
                newInput = userInput[1].split(' ', 1)
                if len(newInput) == 2:
                    myBot.add_due(newInput[0], newInput[1])

        elif (userInput[0].lower() == 'members'):
            myBot.get_group_info(GROUP_ID)

        elif (userInput[0].lower() == 'kick'):
            if len(userInput)  == 2:
                myBot.kick(userInput[1], GROUP_ID)
            else:
                print(f"{Fore.RED}NO NAME PROVIDED")

        elif (userInput[0].lower() == 'add'):
            #print("add command called")
            myBot.add("84913382", "TestName", GROUP_ID)

        elif (userInput[0].lower() == 'help'):
            displayHelp()

        elif (userInput[0].lower() == 'rmdue'):
            if len(userInput) == 2:
                myBot.remove_due(userInput[1])
        else:
            print(f"{Fore.RED}Command Not Recognized")

        userInput = getInput()

    # Stop command issued
    time = datetime.datetime.now()
    print(f"{Fore.RED}<{time}>: Program Terminated")



