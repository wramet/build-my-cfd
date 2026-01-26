#!/usr/bin/env python3
"""
List available models from Z.ai proxy to identify correct DeepSeek ID.
"""

import os
from openai import OpenAI

# Z.ai API Configuration
API_KEY = os.environ.get("GLM_API_KEY", "eec206be51ce4fa8bb5a6eb1526d1661.9UiI1F2WMSBpyWyv")
BASE_URL = os.environ.get("GLM_BASE_URL", "https://api.z.ai/api/coding/paas/v4/")

def list_models():
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    try:
        print(f"Connecting to {BASE_URL}...")
        models = client.models.list()
        
        print("\nAvailable Models:")
        print("-" * 50)
        
        # Sort for easier reading
        model_list = sorted([m.id for m in models.data])
        
        for model_id in model_list:
            if "deepseek" in model_id.lower() or "glm" in model_id.lower():
                print(f"✅ {model_id}")
            else:
                print(f"  {model_id}")
                
    except Exception as e:
        print(f"\n❌ Error listing models: {e}")

if __name__ == "__main__":
    list_models()
