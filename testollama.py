# from transformers import LlamaTokenizer

# tokenizer = LlamaTokenizer.from_pretrained('path/to/llama3')


# from langchain_community.llms import Ollama

# llm = Ollama(
#     model="llama3"
# )  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `

# response = llm.invoke("Tell me a joke")
# print(response)

# from transformers import PreTrainedTokenizerFast

# available_encodings =  PreTrainedTokenizerFast(tokenizer_file="./tokenizer.json")()
# print(available_encodings)


import json

def fix_json_error(data: str, return_str=True):
    # Strip unnecessary characters and whitespace
    data = data.strip().strip('"').strip(",").strip("`")
    
    # Attempt to add missing closing brackets if necessary
    open_brackets = data.count('{') + data.count('[')
    close_brackets = data.count('}') + data.count(']')
    if open_brackets > close_brackets:
        data += '}' * (open_brackets - close_brackets)
    
    try:
        json.loads(data)
        return data
    except json.decoder.JSONDecodeError:
        data = data.split("\n")
        data = [line.strip() for line in data]
        for i in range(len(data)):
            line = data[i]
            if line in ['[', ']', '{', '}']:
                continue
            if line.endswith(('[', ']', '{', '}')):
                continue
            # Ensure we don't access an out-of-range index
            if i < len(data) - 1 and not line.endswith(',') and data[i + 1] not in [']', '}', '],', '},']:
                data[i] += ','
            # Remove trailing comma if the next line is a closing bracket
            if i < len(data) - 1 and data[i + 1] in [']', '}', '],', '},'] and line.endswith(','):
                data[i] = line[:-1]
        data = "\n".join(data)
        
        # Attempt to load again and catch any remaining errors
        try:
            if not return_str:
                data = json.loads(data)
            return data
        except json.decoder.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON: {e}")

# Example JSON input to test the function
json_input = """
{
    "method": "POST",
    "url": "/gmail/v1/users/me/messages/send",
    "headers": {},
    "body": {
        "raw": "RnJvbTogbW9oYW1lZGhhY2hpY2hhMjAwMUBnbWFpbC5jb20gClRvOiBoYWNoaWNoYS5tb2hhbWVkQGVzcHJpdC50biAKU3ViamVjdDogU2F5aW5nIEhlbGxvIAoKVGhpcyBpcyBhIG1lc3NhZ2UganVzdCB0byBzYXkgaGVsbG8u"
"""

fixed_json = fix_json_error(json_input)
print(fixed_json)
