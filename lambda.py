import json
import re
from datetime import datetime, date
import boto3
import uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HarmonyPeaks')

# Define hotel names and room types
hotels = ['Harmony Peaks Bora Bora', 'Harmony Peaks Imperial', 'Harmony Peaks Deluxe', 'Harmony Peaks Alpine Haven', 'Harmony Peaks Oasis']
room_types = ['Standard room', 'Deluxe room', 'Suite', 'Penthouse', 'Bungalow']

def validate_phone_number(phone):
    # Validate phone number using a regex pattern
    phone_pattern = r"^\+[\d]{1,14}$"
    return re.match(phone_pattern, phone) is not None

def validate_reservation(slots):
    # Validate Hotel
    if not slots['Hotel']:
        return {
            'isValid': False,
            'invalidSlot': 'Hotel',
            'message': 'Which hotel would you like to book a room at?'
        }

    # Validate Room type
    if not slots['Rooms']:
        return {
            'isValid': False,
            'invalidSlot': 'Rooms',
            'message': 'Which room would you like to choose?'
        }
    elif slots['Rooms']['value']['originalValue'] not in room_types:
        return {
            'isValid': False,
            'invalidSlot': 'Rooms',
            'message': 'Invalid room type. Please select from: {}.'.format(", ".join(room_types))
        }

    # Validate CheckIn date
    if not slots['CheckIn']:
        return {
            'isValid': False,
            'invalidSlot': 'CheckIn',
            'message': 'Please provide the Check-in date.'
        }
    else:
        try:
            check_in_date = datetime.strptime(slots['CheckIn']['value']['originalValue'], "%d-%m-%Y")
            today = date.today()
            if check_in_date.date() < today:
                raise ValueError
        except ValueError:
            return {
                'isValid': False,
                'invalidSlot': 'CheckIn',
                'message': 'Invalid date for Check-in. Please provide a date from today onwards in "dd-mm-yyyy" format.'
            }

    # Validate CheckOut date
    if not slots['CheckOut']:
        return {
            'isValid': False,
            'invalidSlot': 'CheckOut',
            'message': 'Please provide the Check-out date.'
        }
    else:
        try:
            check_out_date = datetime.strptime(slots['CheckOut']['value']['originalValue'], "%d-%m-%Y")
            if check_out_date < check_in_date:
                raise ValueError
        except ValueError:
            return {
                'isValid': False,
                'invalidSlot': 'CheckOut',
                'message': 'Invalid date for Check-out. Please provide a date that is after the Check-in date in "dd-mm-yyyy" format.'
            }

    # Validate FirstName, LastName, Email, Phone
    if not slots['FirstName']:
        return {
            'isValid': False,
            'invalidSlot': 'FirstName',
            'message': 'Now I need your data to book this room. Could you please provide your first name?'
        }
    if not slots['LastName']:
        return {
            'isValid': False,
            'invalidSlot': 'LastName',
            'message': 'Could you please provide your last name?'
        }
    if not slots['Email']:
        return {
            'isValid': False,
            'invalidSlot': 'Email',
            'message': 'Could you please provide your email?'
        }
    if not slots['Phone']:
        return {
            'isValid': False,
            'invalidSlot': 'Phone',
            'message': 'Could you please provide your phone number?'
        }
    elif not validate_phone_number(slots['Phone']['value']['originalValue']):
        return {
            'isValid': False,
            'invalidSlot': 'Phone',
            'message': 'Invalid phone number format. Please provide a valid phone number starting with a "+" sign.'
        }

    # If all validations pass
    return {'isValid': True}

def save_reservation_to_dynamodb(slots):
    # Save the reservation details to DynamoDB
    table.put_item(
        Item={
            'Id': str(uuid.uuid4()),  # Unique ID for each reservation
            'Hotel': slots['Hotel']['value']['originalValue'],
            'RoomType': slots['Rooms']['value']['originalValue'],
            'CheckIn': slots['CheckIn']['value']['originalValue'],
            'CheckOut': slots['CheckOut']['value']['originalValue'],
            'FirstName': slots['FirstName']['value']['originalValue'],
            'LastName': slots['LastName']['value']['originalValue'],
            'Email': slots['Email']['value']['originalValue'],
            'Phone': slots['Phone']['value']['originalValue'],
        }
    )

def lambda_handler(event, context):
    print(event)

    # Extract slots and intent name from the event
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

    # Validate reservation details
    reservation_validation_result = validate_reservation(slots)

    # Handle dialog flow
    if event['invocationSource'] == 'DialogCodeHook':
        if reservation_validation_result['isValid']:
            # Delegate dialog back to Lex
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }
                }
            }
        else:
            # Elicit the invalid slot from the user
            response = {
                "sessionState": {
                    "dialogAction": {
                        "slotToElicit": reservation_validation_result['invalidSlot'],
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        "name": intent,
                        "slots": slots
                    }
                },
                "messages": [
                    {
                        "contentType": "PlainText",
                        "content": reservation_validation_result['message']
                    }
                ]
            }

            # Provide options if the invalid slot is Hotel or Rooms
            if reservation_validation_result['invalidSlot'] == 'Hotel':
                response_card_sub_title = "Choose a hotel from the options below:"
                response_card_buttons = [
                    {"text": hotel, "value": hotel} for hotel in hotels[:5]
                ]
                response['messages'].append({
                    "contentType": "ImageResponseCard",
                    "content": "Which hotel would you like to book a room at?",
                    "imageResponseCard": {
                        "title": "Hotel Selection",
                        "imageUrl": "https://harmonypeaksbot.s3.eu-central-1.amazonaws.com/images/logomale.jpg",
                        "subtitle": response_card_sub_title,
                        "buttons": response_card_buttons
                    }
                })

            elif reservation_validation_result['invalidSlot'] == 'Rooms':
                response_card_sub_title = "Choose a room type from the options below:"
                response_card_buttons = [
                    {"text": room_type, "value": room_type} for room_type in room_types
                ]
                response['messages'].append({
                    "contentType": "ImageResponseCard",
                    "content": "Which room would you like to choose?",
                    "imageResponseCard": {
                        "title": "Room Selection",
                        "imageUrl": "https://harmonypeaksbot.s3.eu-central-1.amazonaws.com/images/logomale.jpg",
                        "subtitle": response_card_sub_title,
                        "buttons": response_card_buttons
                    }
                })

    # Handle fulfillment
    elif event['invocationSource'] == 'FulfillmentCodeHook':
        if reservation_validation_result['isValid']:
            save_reservation_to_dynamodb(slots)
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Close"
                    },
                    "intent": {
                        "name": intent,
                        "slots": slots,
                        "state": "Fulfilled"
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "Okay, I have booked your room at {}.".format(slots['Hotel']['value']['originalValue'])
                        },
                        {
                            "contentType": "PlainText",
                            "content": "See you in our hotel!"
                        }
                    ]
                }
            }
        else:
            # Handle unexpected failure
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Close"
                    },
                    "intent": {
                        "name": intent,
                        "slots": slots,
                        "state": "Failed"
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "Ooops, something went wrong!"
                        }
                    ]
                }
            }

    print(response)
    return response
