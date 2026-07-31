import os
import smtplib
from email.message import EmailMessage
import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel

def send_email(routine: str) -> str:
    """Sends the generated fitness routine via email."""
    smtp_username = os.environ.get("SMTP_USERNAME")
    # Clean the app password to remove spaces just in case
    smtp_password = os.environ.get("SMTP_PASSWORD", "").replace(" ", "")
    target_email = os.environ.get("TARGET_EMAIL")
    
    if not smtp_username or not smtp_password or not target_email:
        return "Failed: SMTP_USERNAME, SMTP_PASSWORD, or TARGET_EMAIL environment variables not set."
        
    msg = EmailMessage()
    msg.set_content(f"Here is your daily fitness routine:\n\n{routine}")
    msg['Subject'] = 'Your Daily Bodyweight Routine'
    msg['From'] = smtp_username
    msg['To'] = target_email
    
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
    
    try:
        project_id = os.environ.get("PROJECT_ID")
        region = os.environ.get("REGION")
        
        # Initialize Vertex AI for the Google Cloud project
        vertexai.init(project=project_id, location=region)
        
        # Use Gemini 1.5 Flash (fast, smart, and cost-effective)
        model = GenerativeModel("gemini-1.5-flash-001")
        
        prompt = (
            "You are a fitness coach. Create a unique daily bodyweight routine. "
            "Requirements:\n"
            "- It must be a HIIT routine: 40 seconds of exercise, 20 seconds of rest, for 20 minutes total.\n"
            "- Include a 5-minute warm-up using jump ropes or similar cardio movements.\n"
            "- 2 or 3 times a week, provide an alternative option like: 'Follow this workout, or alternatively go for a 30-minute run', while still providing the full HIIT workout.\n"
            "- Include a description of the muscle groups engaged.\n"
            "- Include an estimated calorie burn for a man weighing above 90kg.\n"
            "Format the response cleanly in plain text."
        )
        
        response = model.generate_content(prompt)
        routine = response.text
        
        email_status = send_email(routine)
        return f"Routine generated. {email_status}", 200
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error generating routine: {e}", 500
