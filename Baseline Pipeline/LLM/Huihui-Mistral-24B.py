from llama_cpp import Llama

# Load model
llm = Llama(model_path="Huihui-Mistral-Small-3.2-24B-Instruct-2506-abliterated-llamacppfixed.Q4_K_S.gguf", n_ctx=2048, temperature=0.7)

prompt = "<|im_start|>user\nHello! How are you today?<|im_end|>\n<|im_start|>assistant\n"

resp = llm(prompt, max_tokens=200, stop=["<|im_end|>", "<|im_start|>"])
text = resp['choices'][0]['text']

print("Response:", text)
