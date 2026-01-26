import os
import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from openai import OpenAI
import uvicorn

app = FastAPI()

# Load Config
CONFIG_PATH = "litellm_config.yaml"
MODELS = {}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"Config not found: {CONFIG_PATH}")
        return
    
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
        
    for m in data.get("model_list", []):
        name = m.get("model_name")
        params = m.get("litellm_params", {})
        MODELS[name] = params
        print(f"🔹 Loaded Route: {name} -> {params.get('model')} ({params.get('api_base')})")

load_config()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/models")
async def list_models():
    data = []
    for name in MODELS:
        data.append({
            "id": name,
            "object": "model",
            "created": 1677610602,
            "owned_by": "openai"
        })
    return {"object": "list", "data": data}

@app.post("/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
         # Handle case where body might be empty or malformed
         raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model")
    
    # Routing Logic
    if model_name not in MODELS:
        # Fallback: try to find a matching prefix or just error
        # Check for deepseek-coder mapping specifically if alias not exact
        if "deepseek" in model_name:
             target_config = MODELS.get("deepseek-coder") or MODELS.get("deepseek-chat")
        elif "claude" in model_name:
             target_config = MODELS.get("claude-3-5-sonnet-20241022")
        else:
             raise HTTPException(status_code=400, detail=f"Model {model_name} not found in config.")
    else:
        target_config = MODELS[model_name]
    
    if not target_config:
         raise HTTPException(status_code=400, detail=f"No route for model {model_name}")

    # Prepare Client
    api_key = target_config.get("api_key")
    base_url = target_config.get("api_base")
    target_model = target_config.get("model")
    
    # Remove 'openai/' prefix if present in target model name (common litellm convention)
    if target_model.startswith("openai/"):
        target_model = target_model.replace("openai/", "")
    if target_model.startswith("deepseek/"):
        target_model = target_model.replace("deepseek/", "")

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print(f"🔀 Routing {model_name} -> {target_model} at {base_url}")
    
    # Clean body for forwarding
    # Remove 'model' from body as we pass it explicitly? No, OpenAI client needs it.
    # We update the model name to the TARGET model name
    body["model"] = target_model
    
    # Check for stream
    is_stream = body.get("stream", False)
    
    try:
        val = client.chat.completions.create(**body)
        if is_stream:
             # Just return it directly if library handles it (it returns a Stream object)
             # We need to yield bytes
             def iter_stream():
                 for chunk in val:
                     yield f"data: {chunk.model_dump_json()}\n\n"
                 yield "data: [DONE]\n\n"
             return StreamingResponse(iter_stream(), media_type="text/event-stream")
        else:
             return JSONResponse(content=val.model_dump())
             
    except Exception as e:
        print(f"❌ Error forwarding request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, loop="asyncio")
