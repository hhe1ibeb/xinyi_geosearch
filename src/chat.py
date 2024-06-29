from transformers import AutoTokenizer, pipeline
import torch
from src.search import get_search_result, collection
import re

def extract_coordinates_from_suggestion(text):
    # Define the regular expression pattern for latitude and longitude
    lat_pattern = r"Lat:\s*(-?\d+\.\d+)"
    lon_pattern = r"Lon:\s*(-?\d+\.\d+)"
    
    # Search for the patterns in the text
    lat_match = re.search(lat_pattern, text)
    lon_match = re.search(lon_pattern, text)
    
    # Extract the latitude and longitude if found
    if lat_match and lon_match:
        lat = float(lat_match.group(1))
        lon = float(lon_match.group(1))
        return lat, lon
    else:
        return None, None

def extract_coordinates_from_url(url):
    match = re.search(r'/([\d.]+)_([\d.]+)_', url)
    if match:
        return str(match.group(1)), str(match.group(2))
    return None, None

def setup_pipeline(model, device):
    torch_dtype = ""
    if device == "mps":
        torch_dtype = torch.float16
    else:
        torch_dtype = torch.bfloat16

    tokenizer = AutoTokenizer.from_pretrained(model)
    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        model_kwargs={"torch_dtype": torch_dtype},
        device=device
    )

model = "google/gemma-2b-it"
device = "cuda" # mps, cpu, cuda

chat_pipeline = setup_pipeline(model, device)

def answer(query, lang):
    source_information = get_search_result(query, collection, lang)
    instruction = (
        "You are a real estate agent whose job is to suggest the best place to the buyer. "
        "You must explain and support your answer with the provided information. "
        "Answer the user's QUESTION using the DOCUMENT text above. "
        "Keep your answer grounded in the facts of the DOCUMENT. "
        "Remember to return the coordinates of the best place."
    )

    message = [{"role": "user", "content": query},
               {"role": "assistant", "content": f"DOCUMENT:\n{source_information}\n{instruction}"}]

    print(message)

    prompt = chat_pipeline.tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)

    outputs = chat_pipeline(
        prompt,
        max_new_tokens=2048,
        num_return_sequences=1,
    )
    
    return outputs[0]["generated_text"][len(prompt):]