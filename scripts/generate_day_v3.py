import os
import argparse
import sys
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

def generate_content(day, topic, skeleton_path, output_path):
    # Read contexts
    context = read_file("daily_learning/phase_1_context.md")
    template = read_file("daily_learning/templates/deepseek_v3_expand_template.md")
    skeleton = read_file(skeleton_path)

    # Common system prompt
    system_prompt = """You are an expert CFD Engine developer and technical writer. 
    Your task is to expand a JSON skeleton into a comprehensive, "hardcore" technical lesson in Markdown.
    
    CRITICAL REQUIREMENTS:
    1.  **Length:** The output MUST be at least 1500 lines long. Be extremely verbose, detailed, and thorough.
    2.  **Language:** Use "Engineering Thai" (Thai backbone with English technical terms).
    3.  **Content:** Follow the structure defined in the skeleton and template exactly.
    4.  **Format:** Output raw Markdown content only. Do not include markdown fences (```markdown) around the entire file.
    """

    sections = [
        ("1. Frontmatter + Learning Objectives", "Define metadata and 4-6 detailed learning objectives. START with Metadata block."),
        ("2. Section 1: Theory (Theory)", "Write 300+ lines of theory. Include LaTeX equations, tables, and physical explanations."),
        ("3. Section 2: OpenFOAM Reference", "Write 400+ lines analyzing OpenFOAM .H/.C files. Include code snippets and 'What We Do DIFFERENTLY' tables."),
        ("4. Section 3: Class Design", "Write 200+ lines. Include Mermaid diagrams and strict class specifications."),
        ("5. Section 4: Implementation", "Write 400+ lines of C++ code (Header and Implementation files). Must be compilable."),
        ("6. Section 5: Build & Test", "Write 150+ lines. CMakeLists.txt and Unit Tests."),
        ("7. Section 6: Concept Checks", "Write 100+ lines. 4-6 Q&A with deep explanations."),
        ("8. References & Related Days", "List references and links.")
    ]
    
    print(f"🚀 Starting Multi-Stage Generation for Day {day}: {topic}")
    
    # Initialize file (Modified to APPEND/RESUME)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not os.path.exists(output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("")
    else:
        print(f"⚠️ Appending to existing file: {output_path}")

    for section_title, section_prompt in sections:
        print(f"   👉 Generating {section_title}...")
        
        user_prompt = f"""
        Context:
        {context}
        
        Input Skeleton (JSON):
        {skeleton}
        
        CURRENT TASK:
        Write **ONLY** "{section_title}" for Day {day}.
        
        Requirements:
        1. {section_prompt}
        2. Use "Engineering Thai" language.
        3. Do NOT repeat previous sections.
        4. Output Markdown format.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"      ⏳ Attempt {attempt + 1}/{max_retries} (Streaming)...")
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,  # ENABLE STREAMING
                    temperature=0.7,
                    timeout=600.0
                )
                
                full_content = ""
                # Open file for appending chunks in real-time
                with open(output_path, 'a', encoding='utf-8') as f:
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            content_piece = chunk.choices[0].delta.content
                            # Filter markdown fences if they appear at start/end (basic heuristic)
                            if full_content == "" and content_piece.strip().startswith("```markdown"):
                                content_piece = content_piece.replace("```markdown", "", 1)
                            
                            f.write(content_piece)
                            f.flush() # Ensure it's written
                            full_content += content_piece
                            print(f".", end="", flush=True) # Progress indicator
                            
                    f.write("\n\n") # Append spacer after section (INSIDE BLOCK)
                    
                print(f"\n      ✅ Section done ({len(full_content)} chars)")
                break # Success
                
            except Exception as e:
                print(f"\n      ⚠️ Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print(f"      ❌ Failed after {max_retries} attempts. Exiting.")
                    sys.exit(1)
                import time
                time.sleep(5)

    print(f"💾 Completed! Saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Day Content using DeepSeek V3")
    parser.add_argument("--day", required=True, help="Day number (e.g., 01)")
    parser.add_argument("--topic", required=True, help="Topic title")
    parser.add_argument("--skeleton", required=True, help="Path to skeleton JSON file")
    parser.add_argument("--output", required=True, help="Path to output Markdown file")
    
    args = parser.parse_args()
    
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("❌ Error: DEEPSEEK_API_KEY environment variable not set.")
        sys.exit(1)
        
    generate_content(args.day, args.topic, args.skeleton, args.output)
