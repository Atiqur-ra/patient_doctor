import google.generativeai as genai
import os
from dotenv import load_dotenv
from better_profanity import profanity

load_dotenv()
genai.configure(api_key= os.getenv("GEMNI_API"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
profanity.load_censor_words()

   
def analyze_comment_with_gemini(comment: str) -> int:
    if profanity.contains_profanity(comment):
        return 1
    prompt = f"Rate this doctor review from 1 (bad) to 5 (excellent): '{comment}'. Just output the numerical rating."

    response = model.generate_content(prompt)
    rating_text = response.text.strip()
    
    try:
        rating = float(rating_text)
        return min(max(rating, 1), 5)
    except:
        return 1
    

