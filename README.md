# Hotel reservation chatbot Project

## Overview
The Harmony Peaks Chatbot Project involves creating an AWS Lambda function and an Amazon Lex bot to handle hotel reservation inquiries at Harmony Peaks. The Lex bot interacts with users to gather reservation details, which are then validated by the Lambda function and stored in DynamoDB.

## Usage
1. Interact with the Bot: Start a conversation with the Lex bot and provide the necessary reservation details (date, time, number of guests).
2. Validation: The bot sends the details to the Lambda function for validation.
3. Response: Based on the validation, the bot either confirms the reservation or asks for corrected details.
4. Storage: Valid reservation details are stored in a DynamoDB table.
