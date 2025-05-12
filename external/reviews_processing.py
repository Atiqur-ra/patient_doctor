import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key= os.getenv("GEMNI_API"))
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

   
def analyze_comment_with_gemini(comment: str) -> int:
    prompt = f"Rate this doctor review from 1 (bad) to 5 (excellent): '{comment}'. Just output the numerical rating."

    response = model.generate_content(prompt)
     # Extract the rating from the response
    rating_text = response.text.strip()
    
    try:
        rating = int(rating_text.strip())
        return min(max(rating, 1), 5)
    except:
        return 3
    

