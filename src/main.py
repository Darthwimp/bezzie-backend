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
    try:
        user_query = request.query
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": "you are an assitant"},
                {"role": "user", "content": user_query}
            ]
        )
        
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    
    from pyngrok import ngrok
    ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
    public_url = ngrok.connect(8000, url="cheerful-fish-slowly.ngrok-free.app")
    print(f"\033[94mPublic URL: {public_url.public_url}\033[0m")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    