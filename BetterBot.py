import datetime
import json
import random
import string
from math import ceil

import requests
from colorama import init

init(autoreset=True)
from colorama import Fore

BASE_URL = 'https://v2.groupme.com/groups/'

MSGS_PER_PAGE = 20

MASTER_FILE = "masterList"
COMMANDS = "commands"
MEMBER_FILE = "members"
ACCESS_TOKEN_LINK = "https://v2.groupme.com/access_tokens"


class BetterBot:

    # authToken is public-ish token used, hashedToken is a tocken created via
    # unknown hash
    def __init__(self, userName, password):
        self.sesh = requests.session()
        self.hashedToken = ""
        self.authToken = ""
        self.__get_token(userName, password)

    # Parses through the desired chat
    def save_messages(self, groupID, filename=MASTER_FILE):
        # Create endpoint
        endpoint = BASE_URL + groupID + '/messages'

        # Headers that contains the groupId again, and now the unhashed auth token
        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Charset': 'ISO-8859-1,utf-8',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Origin': 'https://web.groupme.com',
            'Referer': 'https://web.groupme.com/groups/' + groupID,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
            'X-Access-Token': self.authToken
        }

        # Getting initial set of data
        params = {}
        r = self.sesh.get(endpoint, params=params, headers=headers)

        msg = json.loads(r.text)

        # Total number of msgs
        totalMsgCount = msg.get('response').get('count')

        # Number of needed iterations
        totalIterations = ceil((totalMsgCount / MSGS_PER_PAGE))

        # Display number of messages to be parsed
        time = datetime.datetime.now()
        print("{}<{}> {}Parsing {}{}{} total messages".format(Fore.RED, time, Fore.GREEN,
                                                              Fore.BLUE, totalMsgCount, Fore.GREEN))

        with open(filename + ".json", 'w') as bigFile:
            with open('READABLE_' + filename, 'w') as smallFile:
                bigFile.write("{\n")

                # Iterate through the pages in sets of 20
                counter = totalMsgCount - 1
                for i in range(totalIterations):

                    # Send in a request to get the msgs
                    r = self.sesh.get(endpoint, params=params, headers=headers)
                    msg = json.loads(r.text)

                    # Calculate the last msg received
                    last_id = msg.get('response').get('messages')[-1].get('id')

                    # Set the last msg recived
                    params = {'before_id': last_id}

                    # Iterate through each msg, textDict is a dict
                    for textDict in msg['response']['messages']:
                        # Dump to large file with indents
                        bigFile.write(f"\"MSG_NUM_{counter}\":")
                        bigFile.write(json.dumps(textDict, indent=2) + ",")

                        # Dump to human readable file
                        textAdd = "<{}> {} said: {}".format(textDict.get('created_at'), textDict.get('name'),
                                                            textDict.get('text'))
                        smallFile.write(textAdd + '\n')
                        counter -= 1
                bigFile.write("\n}")

    # Sends a msg into the group
    def say(self, text, groupID):

        text = "BOT:  " + text
        endpoint = BASE_URL + groupID + '/messages'

        source_guid = ''.join(random.choice(string.ascii_lowercase
                                            + string.digits) for _ in range(30))

        mycoolpayload = '{"message":{"text":"' + text + \
                        '","attachments":[],"source_guid":"' + source_guid + '"}}'

        myTestHead = {'accept': 'application/json, text/plain, */*',
                      'accept-encoding': 'gzip, deflate, br',
                      'accept-language': 'en-US,en;q=0.9',
                      'content-length': '100',
                      'content-type': 'application/json;charset=UTF-8',
                      'origin': 'https://web.groupme.com',
                      'referer': 'https://web.groupme.com/',
                      'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                      'sec-ch-ua-mobile': '?0',
                      'sec-ch-ua-platform': 'macOS',
                      'sec-fetch-dest': 'empty',
                      'sec-fetch-mode': 'cors',
                      'sec-fetch-site': 'same-site',
                      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                      'x-access-token': self.hashedToken}
        self.sesh.headers = myTestHead
        r = self.sesh.post(endpoint, data=mycoolpayload)

    # Displays Due Dates
    def display_dues(self, groupID):

        # Open the command file
        with open(COMMANDS, 'r') as commandFile:
            file = json.load(commandFile)

            # Load the dues command
            due_data = file.get("command_data").get("!due")

            # Iterate through all dues, add to master string
            send_msg = "\\nDue Dates:"

            for dueDate in due_data:
                # add each assignment, formatted, to master string
                send_msg += "\\nAssignment: " + dueDate.get("Item_Name") + \
                            "\\n-Due Date: " + dueDate.get("Due_Date")
            # Send the msg
            self.say(send_msg, groupID)
        commandFile.close()

    # Adds a due date by taking in the command file, editing the python dict, then re-writing the file
    def add_due(self, name, date):

        with open(COMMANDS, 'r') as command_File:
            commandFile = json.load(command_File)
        command_File.close()

        with open(COMMANDS, 'w') as command_file:
            dues = commandFile.get("command_data").get("!due")
            new_due = {"Item_Name": name, "Due_Date": date}

            dues.append(new_due)

            commandFile["command_data"]["!due"] = dues

            command_file.write(json.dumps(commandFile, indent=2))
        command_file.close()

    # Removes the supplied due from the stored due list
    def remove_due(self, name):

        # Open the command file
        with open(COMMANDS, 'r') as cmdFile:
            commands = json.load(cmdFile)
        cmdFile.close()

        with open(COMMANDS, 'w') as cmdFile:
            newDues = []

            # Iterate through all assignments
            for due in commands.get("command_data").get("!due"):
                # Only add dues that are not the target of removal
                if due.get("Item_Name") != name:
                    newDues.append(due)
            commands["command_data"]["!due"] = newDues

            cmdFile.write(json.dumps(commands, indent=2))
        cmdFile.close()


    # Grabs information about the group, mainly member information
    def groupInfo(self, groupID):
        myTestHead = {'accept': 'application/json, text/plain, */*',
                      'accept-encoding': 'gzip, deflate, br',
                      'accept-language': 'en-US,en;q=0.9',
                      'content-length': '100',
                      'content-type': 'application/json;charset=UTF-8',
                      'origin': 'https://web.groupme.com',
                      'referer': 'https://web.groupme.com/',
                      'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
                      'sec-ch-ua-mobile': '?0',
                      'sec-ch-ua-platform': 'macOS',
                      'sec-fetch-dest': 'empty',
                      'sec-fetch-mode': 'cors',
                      'sec-fetch-site': 'same-site',
                      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                      'x-access-token': self.hashedToken}

        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Charset': 'ISO-8859-1,utf-8',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Origin': 'https://web.groupme.com',
            'Referer': 'https://web.groupme.com/groups/' + groupID,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
            'X-Access-Token': self.authToken
        }

        self.sesh.headers = headers

        group = self.sesh.get(BASE_URL + groupID, headers=headers)
        data = json.loads(group.text)
        with open("MEMBERS.json", 'w') as temp:
            temp.write(json.dumps(data, indent=2))
        temp.close()

    # Gets GROUP and Members information
    def get_group_info(self, groupID):
        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Charset': 'ISO-8859-1,utf-8',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Origin': 'https://web.groupme.com',
            'Referer': 'https://web.groupme.com/groups/' + groupID,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
            'X-Access-Token': self.authToken
        }

        group = self.sesh.get(BASE_URL + groupID, headers=headers)
        data = json.loads(group.text)
        with open(MEMBER_FILE + ".json", 'w') as temp:
            temp.write(json.dumps(data, indent=2))
        temp.close()

    # Kicks the given user
    def kick(self, name, groupID):
        membershipID = str(self.__get_membershipID(name, groupID))

        # ID found, proceed with kick
        if membershipID:

            headers = {
                'Accept': 'application/json, text/javascript',
                'Accept-Charset': 'ISO-8859-1,utf-8',
                'Accept-Language': 'en-US',
                'Content-Type': 'application/json',
                'Origin': 'https://web.groupme.com',
                'Referer': 'https://web.groupme.com/groups/' + groupID,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
                'X-Access-Token': self.authToken
            }

            endpoint = BASE_URL + groupID + "/memberships/" + membershipID + "/destroy"

            d = self.sesh.post(endpoint, headers=headers)
        else:
            print(f"{Fore.RED}CANNOT FIND MEMBER: {name}")

    # Adds the user with userID and assigns a nickname
    def add(self, userID, nickname, groupID):

        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Charset': 'ISO-8859-1,utf-8',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Origin': 'https://web.groupme.com',
            'Referer': 'https://web.groupme.com/groups/' + groupID,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
            'X-Access-Token': self.authToken
        }

        endpoint = BASE_URL + groupID + "/members/add"
        # params = {"members": [{"nickname": "Test", "user_id": f"{userID}", "guid": "testguid"}]}
        params = '{"members": [{"nickname": "' + nickname + '", "user_id": "' + userID + '", "guid": "testguid"}]}'
        endpoint = "https://api.groupme.com/v3/groups/GROUPID/members/add"
        self.sesh.headers = headers

        d = self.sesh.post(endpoint, data=params)



    # Returns the membershipIP of the supplied username - used for the kick function
    # This method needs a working members file to get the membership ID
    def __get_membershipID(self, userName, groupID):

        # Update the members file
        self.get_group_info(groupID)

        # Get the membership ID
        with open(MEMBER_FILE + ".json", 'r') as memberFile:
            members = json.load(memberFile)
            members = members.get("response").get("group").get("memberships")
        memberFile.close()
        for person in members:
            # Check if we can find the username
            if person.get("name") == userName:
                # Return their membership ID
                return person.get("id")
        return False

    def __get_token(self, userName, password):
        print(f"{Fore.GREEN}Attempting to login BetterBot")

        endpoint = ACCESS_TOKEN_LINK

        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Charset': 'ISO-8859-1,utf-8',
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
            'Origin': 'https://web.groupme.com',
            'Referer': 'https://web.groupme.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
            'X-Access-Token': ""
        }

        payload = '{"username": "' + userName + '", "password": "' + password + '", "grant_type":"password",' \
                                                                                '"app_id":"groupme-web",' \
                                                                                '"device_id' \
                                                                                '":""} '

        # Set headers and send payload to endpoint
        self.sesh.headers = headers
        d = self.sesh.post(endpoint, data=payload)

        # Catch response and parse it for the token

        response = json.loads(d.text)
        print(d.text)

        try:
            token = response.get("response", "error").get("access_token")
            self.hashedToken = token
            self.authToken = token
            print(token)
            print(f"{Fore.GREEN}Grabbed Token, BetterBot logged in")
        except Exception as e:
            print(f"{Fore.RED}ERROR WHEN ATTEMPTING TO GRAB TOKEN")
            exit(-1)

