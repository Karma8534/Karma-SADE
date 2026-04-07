# Conversation state _ OpenAI API

*Converted from: Conversation state _ OpenAI API.PDF*


create a threaded conversation.
Chain responses across turns by passing the previous response ID python
1 from openai import OpenAI
2 client = OpenAI()
3
4 response = client.responses.create(
5 model="gpt-4o-mini",
6 input="tell me a joke",
7 )
8 print(response.output_text)
9
10 second_response = client.responses.create(
11 model="gpt-4o-mini",
12 previous_response_id=response.id,
13 input=[{"role": "user", "content": "explain why this is funny."}],
14 )
15 print(second_response.output_text)
In the following example, we ask the model to tell a joke. Separately, we ask the model to
explain why it’s funny, and the model has all necessary context to deliver a good response.
Manually manage conversation state with the Responses API python
1 from openai import OpenAI
2 client = OpenAI()
3
4 response = client.responses.create(
5 model="gpt-4o-mini",
6 input="tell me a joke",
7 )
8 print(response.output_text)
9
10 second_response = client.responses.create(
11 model="gpt-4o-mini",
12 previous_response_id=response.id,
13 input=[{"role": "user", "content": "explain why this is funny."}],
14 )
15 print(second_response.output_text)
Data retention for model responses
Even when using previous_response_id , all previous input tokens for responses in the
chainarebilledasinputtokensintheAPI