import os
import argparse
import sys
import re
from openai import OpenAI

# Initialize client with DeepSeek base URL
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)

def generate_skeleton(day, topic, output_path):
    # Read contexts and templates
    context = read_file("daily_learning/phase_1_context.md")
    template = read_file("daily_learning/templates/deepseek_r1_template.md")

    system_prompt = """You are an expert CFD Engine developer. 
    Your task is to generate a comprehensive JSON skeleton for a daily technical lesson.
    
    CRITICAL INSTRUCTIONS:
    1.  **Output Format:** RETURN JSON ONLY. No markdown conversational text.
    2.  **Content:** Follow the structure of the provided template EXACTLY.
    3.  **Depth:** Ensure the content plan supports a "hardcore" lesson of 1500+ lines.
    """
    
    user_prompt = f"""
    Context:
    {context}
    
    Template (JSON Structure):
    {template}
    
    CURRENT TASK:
    Generate the JSON Skeleton for:
    **Day {day}: {topic}**
    
    Requirements:
    - The JSON must be valid.
    - It must cover all sections defined in the template.
    - For Day {day}, specifically focus on: {topic}
    """
    
    print(f"🧠 Generatng Skeleton for Day {day}: {topic} using DeepSeek R1...")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # V3 (Faster)
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            timeout=300.0
        )
        
        print("      ⏳ Streaming response", end="", flush=True)
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                print(".", end="", flush=True)
        print("\n")
        
        # content is already populated from the loop above
        
        # Extract JSON if wrapped in markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            # Try to find the first '{' and last '}'
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                json_content = content[start:end]
            else:
                json_content = content # Hope it's raw JSON

        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
            
        print(f"✅ Skeleton saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error generating skeleton: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Day Skeleton using DeepSeek R1")
    parser.add_argument("--day", required=True, help="Day number (e.g., 03)")
    parser.add_argument("--topic", required=True, help="Topic title")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    
    args = parser.parse_args()
    
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("❌ Error: DEEPSEEK_API_KEY environment variable not set.")
        sys.exit(1)
        
    generate_skeleton(args.day, args.topic, args.output)
