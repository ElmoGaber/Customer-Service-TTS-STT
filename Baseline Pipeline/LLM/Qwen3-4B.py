from llama_cpp import Llama
import re, json

# Load model
llm = Llama(model_path="Qwen3-4B-Function-Calling-Pro.gguf", n_ctx=2048, temperature=0.7)

# Prompt
prompt = "<|im_start|>user\nGet weather for Paris<|im_end|>\n<|im_start|>assistant\n"

# Generate
resp = llm(prompt, max_tokens=200, stop=["<|im_end|>", "<|im_start|>"])
text = resp['choices'][0]['text']

# Extract tool calls
matches = re.findall(r'\[.*?\]', text)
tool_calls = []
for m in matches:
    try: tool_calls.extend(json.loads(m))
    except: pass

print("Response:", text)
print("Tool Calls:", tool_calls)
