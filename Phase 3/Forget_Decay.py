api = "m0-ZVsvpa9gOcp0RecmUQs9GFNS6AF5PAhm7LaTRuYY"

from mem0 import MemoryClient

client = MemoryClient(api_key=api)

# result = client.add(
#     messages=[
#         {"role": "user", "content": "I just moved to Avengers Tower from New York."},
#         {"role": "assistant", "content": "Got it, I'll update your location."}
#     ],
#     user_id="Bob",
#     metadata={"source" : "onboarding"}
# )
# print(result)

page = client.get_all(filters={"user_id": "alice"}, page=1, page_size=1)
print(page["count"], len(page["results"]))