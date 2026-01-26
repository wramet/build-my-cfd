import sys
import os
import subprocess

def split_text(text, chunk_size=80):
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    
    for line in lines:
        current_chunk.append(line)
        if len(current_chunk) >= chunk_size and (line.strip() == "" or line.startswith("#")):
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    return chunks

def translate_chunk(chunk, chunk_id):
    prompt = """You are a Senior CFD Engineer and Technical Translator.
Task: Translate this partial Markdown content into 'Engineering Thai'.
Rules:
1. Tone: Professional, Instructional.
2. Vocab: Keep TECHNICAL TERMS in English. Do not transliterate.
3. Headers: Bilingual `## English | ไทย`.
4. Formatting: Keep LaTeX and Code UNTOUCHED.
5. Structure: Preserve Markdown structure.
6. Output: ONLY the translated content. No preamble.
"""
    cmd = ["llm", "-m", "deepseek-chat", "-s", prompt]
    try:
        process = subprocess.run(cmd, input=chunk, text=True, capture_output=True, check=True)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error translating chunk {chunk_id}: {e.stderr}", file=sys.stderr)
        return chunk  # Return original if failed

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 split_translate.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        content = f.read()

    chunks = split_text(content)
    print(f"Split {input_file} into {len(chunks)} chunks.")

    translated_content = []
    for i, chunk in enumerate(chunks):
        print(f"Translation chunk {i+1}/{len(chunks)}...", file=sys.stderr)
        trans = translate_chunk(chunk, i)
        translated_content.append(trans)

    # Construct Output Filename
    # Input: daily_learning/drafts/day03_part2.md
    # Output: daily_learning/drafts/day03_thai_part2.md
    dirname = os.path.dirname(input_file)
    basename = os.path.basename(input_file)
    
    if 'thai' in basename:
        output_basename = basename # Already thai
    else:
        output_basename = basename.replace('part', 'thai_part')
    
    output_file = os.path.join(dirname, output_basename)

    with open(output_file, 'w') as f:
        f.write('\n'.join(translated_content))

    print(f"Done. Saved to {output_file}")

if __name__ == "__main__":
    main()
