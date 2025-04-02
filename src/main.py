from email import message
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryRequest(BaseModel):
    query: str
    
@app.get('/ping')
async def ping():
    return {"message": "pong"}
    
@app.post("/send-message")
async def send_message(request: QueryRequest):
    bezziePrompt = """You are a friendly and supportive virtual psychiatrist designed to help users talk about their feelings, challenges, and mental well-being in a safe and non-judgmental space. Your goal is to listen attentively, provide thoughtful responses, and guide the conversation in a calming and reassuring way.
    Always maintain a warm and empathetic tone.
    Encourage users to express themselves without pressure.
    Ask open-ended but gentle questions to help them reflect on their thoughts and emotions.
    Do not diagnose, prescribe medication, or provide medical advice. Instead, offer general mental health insights and coping strategies.
    If a user is in distress, gently encourage them to seek professional help or reach out to a trusted friend or family member.
    Never overwhelm the user with too much information or complex psychological terms—keep responses simple and comforting.
    Be positive but not dismissive. Validate their emotions and offer words of encouragement.
    Respect privacy and avoid asking for sensitive personal details.
    If a user mentions self-harm or severe distress, respond with concern and suggest seeking immediate help from a qualified professional or a helpline.
    Remember, your role is to be a compassionate listener and gentle guide in the user's mental well-being journey."""
    
    try:
        user_query = request.query
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": bezziePrompt},
                {"role": "user", "content": user_query}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class ChatRequest(BaseModel):
    chat_history: str

@app.post("/analyze-mental-state")
async def analyze_chat(request: ChatRequest):
    try:
        prompt = f"""
        Analyze the following chat between a user and a chatbot. Identify the user's mental state based on the text, emotions, and recurring themes.
        - Summarize the user's mental state in at most **50 bullet points**.
        - Be concise but comprehensive.
        - Avoid assumptions that are not evident from the chat.
        - Identify any stress, anxiety, happiness, or other emotions reflected in the chat.
        - If the chat suggests any urgent psychological concerns, note them without diagnosing.
        - do not repeat the same point in different words.

        Chat History:
        {request.chat_history}

        Now, provide the analysis in bullet points:
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "developer", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        print(response.choices[0].message.content)
        return {"summary": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
if __name__ == "__main__":
    
    from pyngrok import ngrok
    ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
    public_url = ngrok.connect(8000, url="cheerful-fish-slowly.ngrok-free.app")
    print(f"\033[94mPublic URL: {public_url.public_url}\033[0m")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    