from flask import Flask, render_template, request, redirect, url_for, send_file
import requests
import random

app = Flask(__name__)

# Google Gemini API configuration
GEMINI_API_KEY = "AIzaSyCjeWAsyXA24ercu7XRISggxH0_Fzf68Kw"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta2/models/gemini/text:generate?key={GEMINI_API_KEY}"

def call_gemini_api_with_variation(prompt_text, temperature=0.9):
    """
    Calls the Gemini LLM API with a specified temperature to encourage more randomness.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {"text": prompt_text},
        "temperature": temperature,  # Higher temperature for more creative responses
        "maxOutputTokens": 10
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0].get("output", prompt_text + " (No refinement)")
            else:
                return prompt_text + " (No candidates returned)"
        else:
            return prompt_text + " (Refinement failed: " + str(response.status_code) + ")"
    except Exception as e:
        return prompt_text + f" (Exception: {e})"

def get_refined_prompts(user_prompt):
    """
    Generates five distinct refined prompts by calling the Gemini-LLM API five times,
    each time using a completely different instruction to rephrase and refine the prompt.
    The instructions emphasize improving clarity, specificity, length, context, and structure.
    """
    # List of distinct base instructions with entirely different wording.
    base_instructions = [
        f"Paraphrase the prompt completely using alternative vocabulary and sentence structure to make it engaging. Original prompt: '{user_prompt}'",
        f"Recast the following prompt into an innovative query with a fresh perspective and completely different wording, while preserving its essential meaning: '{user_prompt}'",
        f"Reformulate the prompt by expressing it in an entirely new way using varied expressions and terminology to enhance clarity and originality. Original prompt: '{user_prompt}'",
        f"Convert the prompt into a new form with unique phrasing and structure that makes it vivid and distinct. Original prompt: '{user_prompt}'",
        f"Generate an alternative version of the prompt with completely different words and sentences, focusing on creative language and originality. Original prompt: '{user_prompt}'"
    ]
    
    refined_prompts = []
    # Shuffle to add extra randomness.
    random.shuffle(base_instructions)
    
    for instruction in base_instructions:
        refined = call_gemini_api_with_variation(instruction, temperature=0.9)
        refined_prompts.append(refined)
    
    return refined_prompts

def evaluate_prompts(prompts):
    """
    Simulates the evaluation of each prompt using four key performance metrics:
      - Perplexity-Faithfulness (lower is better)
      - Token Usage (lower is better)
      - ROUGE (higher is better)
      - BERTScore (higher is better)
    
    Lower-is-better metrics are inverted so that a higher composite score indicates a better refined prompt.
    """
    evaluations = []
    for prompt in prompts:
        # Simulated scores for demonstration.
        perplexity_faithfulness = random.uniform(0, 1)
        token_usage = random.uniform(0, 1)
        rouge = random.uniform(0, 1)
        bert_score = random.uniform(0, 1)

        normalized_perplexity = 1 - perplexity_faithfulness
        normalized_token_usage = 1 - token_usage

        composite_score = (normalized_perplexity + normalized_token_usage + rouge + bert_score) / 4
        evaluations.append((prompt, composite_score))
    return evaluations

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/refine", methods=["POST"])
def refine():
    user_prompt = request.form.get("prompt")
    if not user_prompt:
        return redirect(url_for("index"))
    
    # Generate 5 distinct refined prompts via separate Gemini-LLM calls.
    refined_prompts = get_refined_prompts(user_prompt)
    evaluations = evaluate_prompts(refined_prompts)
    
    # Sort by composite score in descending order.
    evaluations.sort(key=lambda x: x[1], reverse=True)
    recommended_prompt = evaluations[0][0]
    
    return render_template("results.html",
                           refined_prompts=refined_prompts,
                           original_prompt=user_prompt,
                           recommended_prompt=recommended_prompt)

@app.route("/select", methods=["POST"])
def select():
    chosen_prompt = request.form.get("chosen_prompt")
    return render_template("select.html", chosen_prompt=chosen_prompt)

@app.route("/export", methods=["POST"])
def export():
    chosen_prompt = request.form.get("chosen_prompt")
    export_format = request.form.get("export_format")
    
    if export_format == "txt":
        from io import BytesIO
        content = chosen_prompt
        file_obj = BytesIO()
        file_obj.write(content.encode("utf-8"))
        file_obj.seek(0)
        return send_file(file_obj, as_attachment=True, download_name="prompt.txt", mimetype="text/plain")
    
    elif export_format == "pdf":
        try:
            from fpdf import FPDF
        except ImportError:
            return "FPDF library is not installed. Cannot export as PDF."
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, chosen_prompt)
        from io import BytesIO
        # Output the PDF to a string, then encode it and write it into a BytesIO object.
        pdf_str = pdf.output(dest="S")
        pdf_bytes = BytesIO(pdf_str.encode("latin1"))
        pdf_bytes.seek(0)
        return send_file(pdf_bytes, as_attachment=True, download_name="prompt.pdf", mimetype="application/pdf")
    
    else:
        return "Invalid export format selected.", 400

if __name__ == "__main__":
    app.run(debug=True)
