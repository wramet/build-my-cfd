import os
import uvicorn
import yaml
import litellm.proxy.proxy_server as proxy_server_module
from litellm.proxy.proxy_server import app, proxy_config, llm_router
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Force Config Path
default_config = "litellm_config.yaml"
config_path = os.getenv("LITELLM_CONFIG_PATH", os.path.abspath(default_config))
proxy_server_module.user_config_file_path = config_path

print(f"🚀 Starting LiteLLM Proxy manually with config: {config_path}")

# Manually load config to be safe
try:
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    
    if config_data and "model_list" in config_data:
        print(f"✅ Loaded config data keys: {list(config_data.keys())}")
        
        # 1. Update Proxy Config
        proxy_config.config = config_data
        proxy_config.model_list = config_data["model_list"]
        
        # 2. Update Router STRICTLY
        if llm_router is not None:
            print("✅ Initializing llm_router with model list...")
            llm_router.set_model_list(config_data["model_list"])
        else:
            print("⚠️ llm_router is None! Attempting to force initialization.")
            from litellm import Router
            proxy_server_module.llm_router = Router(model_list=config_data["model_list"])
            print("✅ Forced initialization of llm_router")

except Exception as e:
    print(f"❌ Failed to load config manually: {e}")

# ==========================================
# MOCK ANTHROPIC ENDPOINTS FOR CLI COMPATIBILITY
# ==========================================

@app.api_route("/api/hello", methods=["GET", "POST"])
async def mock_hello(request: Request):
    print("👋 Mocking /api/hello")
    return JSONResponse(status_code=200, content={"message": "Hello from LiteLLM Proxy!"})

@app.api_route("/api/claude_cli_profile", methods=["GET", "POST"])
async def mock_profile(request: Request):
    print("👤 Mocking /api/claude_cli_profile")
    # Return a dummy profile that satisfies the CLI
    return JSONResponse(status_code=200, content={
        "uuid": "mock-uuid",
        "email": "user@example.com",
        "name": "Local Proxy User",
        "settings": {}
    })

@app.api_route("/api/event_logging/batch", methods=["GET", "POST"])
async def mock_logging(request: Request):
    # Silence logging errors
    return Response(status_code=200)

@app.api_route("/api/eval/{path:path}", methods=["GET", "POST"])
async def mock_eval(path: str, request: Request):
    print(f"🧪 Mocking eval: {path}")
    return Response(status_code=404) # Let's keep 404 for unknown evals, or 200?

# Redirect /v1/messages to proper place is handled by LiteLLM automatically
# But wait, Claude CLI calls /v1/messages OR /api/v1/messages?
# The logs showed "POST /v1/messages" so it's executing correctly against root.

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, loop="asyncio")
