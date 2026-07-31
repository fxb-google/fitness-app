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
            "You are a fitness coach. Create a unique daily bodyweight routine. "
            "Requirements:\n"
            "- It must be a HIIT routine: 40 seconds of exercise, 20 seconds of rest, for 20 minutes total.\n"
            "- Include a 5-minute warm-up using jump ropes or similar cardio movements.\n"
            "- 2 or 3 times a week, provide an alternative option like: 'Follow this workout, or alternatively go for a 30-minute run', while still providing the full HIIT workout.\n"
            "- Include a description of the muscle groups engaged.\n"
            "- Include an estimated calorie burn for a man weighing above 90kg.\n"
            "You must use your send_email tool to send the routine to the user."
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
