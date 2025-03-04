from flask import Flask, render_template, request, redirect, url_for, send_file
import requests  # used for API calls if needed
import random

app = Flask(__name__)

# Replace with your actual GGAIG API endpoint and API key if using the live service.
GGAIG_API_URL = "https://api.google.com/gemini/v1/refine"
API_KEY = "YOUR_API_KEY_HERE"

def get_refined_prompts(user_prompt):
    """
    Simulates a call to the Google-GenerativeAI-Gemini API by returning five distinct
    refined prompt variations based on the user's original prompt.
    """
    refined_prompts = [
        f"Could you elaborate further on '{user_prompt}'?",
        f"In what ways does '{user_prompt}' impact modern technology?",
        f"Discuss the challenges and opportunities related to '{user_prompt}'.",
        f"How can the concept of '{user_prompt}' be applied in real-world scenarios?",
        f"What are the potential benefits and risks associated with '{user_prompt}'?"
    ]
    return refined_prompts

def evaluate_prompts(prompts):
    """
    Simulates the evaluation of each prompt using key performance metrics:
    - Perplexity-Faithfulness (lower is better)
    - Token Usage (lower is better)
    - ROUGE (higher is better)
    - BERTScore (higher is better)

    For lower-is-better metrics we invert the value (1 - metric) so that higher composite scores
    indicate better overall performance.
    """
    evaluations = []
    for prompt in prompts:
        # Simulate metric values between 0 and 1 for each refined prompt.
        perplexity_faithfulness = random.uniform(0, 1)  # Lower is better
        token_usage = random.uniform(0, 1)             # Lower is better
        rouge = random.uniform(0, 1)                   # Higher is better
        bert_score = random.uniform(0, 1)              # Higher is better

        # Normalize lower-is-better metrics by inverting them.
        normalized_perplexity = 1 - perplexity_faithfulness
        normalized_token_usage = 1 - token_usage

        # Composite score is an average of the four metrics.
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
    
    refined_prompts = get_refined_prompts(user_prompt)
    evaluations = evaluate_prompts(refined_prompts)
    
    # Sort the prompts by their composite scores in descending order.
    evaluations.sort(key=lambda x: x[1], reverse=True)
    recommended_prompt = evaluations[0][0]
    
    return render_template("results.html",
                           refined_prompts=refined_prompts,
                           original_prompt=user_prompt,
                           recommended_prompt=recommended_prompt)

@app.route("/select", methods=["POST"])
def select():
    chosen_prompt = request.form.get("chosen_prompt")
    # Render a new template showing the selected prompt and offering export options.
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
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        return send_file(pdf_output, as_attachment=True, download_name="prompt.pdf", mimetype="application/pdf")
    
    else:
        return "Invalid export format selected.", 400

if __name__ == "__main__":
    app.run(debug=True)
