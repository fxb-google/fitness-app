import os
import smtplib
from email.message import EmailMessage
import functions_framework
from google.antigravity import Agent, LocalAgentConfig

def send_email(routine: str) -> str:
    """Sends the generated fitness routine via email."""
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    if not smtp_username or not smtp_password:
        return "Failed: SMTP_USERNAME or SMTP_PASSWORD environment variables not set."
        
    msg = EmailMessage()
    msg.set_content(f"Here is your 25-minute bodyweight routine for today:\n\n{routine}")
    msg['Subject'] = 'Your Daily Bodyweight Routine'
    msg['From'] = smtp_username
    msg['To'] = smtp_username
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

@functions_framework.http
def generate_and_send_routine(request):
    """HTTP Cloud Function entrypoint."""
    
    # Configure the Antigravity Agent
    config = LocalAgentConfig(
        name="FitnessCoach",
        system_prompt=(
            "You are a fitness coach. Your goal is to create a unique 25-minute "
            "bodyweight routine. You must use your send_email tool to send the routine "
            "to the user."
        ),
        tools=[send_email]
    )
    
    agent = Agent(config)
    
    # We trigger the agent to do its job
    # Note: in a real async environment you would await agent.chat(...)
    # but Cloud Functions synchronous python runtime requires running the async loop
    import asyncio
    async def run_agent():
        await agent.chat("Please generate today's 25-minute bodyweight routine and email it to me.")
        
    asyncio.run(run_agent())
    
    return "Routine generated and email process initiated.", 200
