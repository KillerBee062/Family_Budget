from fastapi import FastAPI, Form, Response
import uvicorn
import agent_engine

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Twilio sends a POST request to this endpoint whenever a WhatsApp message is received.
    Body: The text content of the message.
    From: The sender's WhatsApp number.
    """
    print(f"Received message from {From}: {Body}")

    # 1. Process the message using our AI Agent Engine (agent_engine.py)
    # This automatically logs to Supabase if it extracts a transaction.
    try:
        response_text = agent_engine.process_message(Body)
    except Exception as e:
        response_text = f"Sorry, I had trouble processing that: {str(e)}"

    # 2. Respond to Twilio with TwiML (XML)
    # This text will be sent back to the user via WhatsApp.
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{response_text}</Message>
    </Response>"""

    return Response(content=twiml_response, media_type="text/xml")

if __name__ == "__main__":
    # To run this locally: python webhook_agent.py
    # Then use ngrok to expose it: ngrok http 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
