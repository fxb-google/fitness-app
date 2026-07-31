import os
import smtplib
from email.message import EmailMessage
import functions_framework
from google import genai
from google.cloud import firestore

def send_email(routine: str) -> str:
    """Sends the generated fitness routine via email."""
    smtp_username = os.environ.get("SMTP_USERNAME")
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
        api_key = os.environ.get("GEMINI_API_KEY")
        project_id = os.environ.get("PROJECT_ID")
        
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set.", 500
            
        # Initialize Firestore Client
        db = firestore.Client(project=project_id)
        
        # Fetch the last 14 workouts
        workouts_ref = db.collection("workouts").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(14)
        
        history = [doc.to_dict().get("routine", "") for doc in workouts_ref.stream()]
        
        history_text = "\n\n".join([f"--- Workout {i+1} days ago ---\n{routine}" for i, routine in enumerate(history)])
        if not history_text:
            history_text = "No history yet. This is the first workout of the program."

        # Initialize the modern unified Google GenAI SDK
        client = genai.Client(api_key=api_key)
        
        prompt = f"""You are a fitness coach. Create a unique daily bodyweight routine. 
Requirements:
- It must be a HIIT routine: 40 seconds of exercise, 20 seconds of rest, for 20 minutes total.
- Include a 5-minute warm-up using jump ropes or similar cardio movements.
- 2 or 3 times a week, provide an alternative option like: 'Follow this workout, or alternatively go for a 30-minute run', while still providing the full HIIT workout.
- Include a description of the muscle groups engaged.
- Include an estimated calorie burn for a man weighing above 90kg.

Workout History (Last 14 days):
{history_text}

Critically analyze the history above. Design today's workout to specifically target muscle groups that have NOT been heavily focused on recently, ensuring a balanced, dynamic full-body rotation over the weeks. Do not repeat the exact same routines from the history.
Format the response cleanly in plain text without markdown formatting if possible, just clean readable text for an email.
"""
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        
        routine = response.text
        
        # Save the newly generated routine to Firestore
        db.collection("workouts").add({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "routine": routine
        })
        
        email_status = send_email(routine)
        return f"Routine generated and saved to history. {email_status}", 200
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error generating routine: {e}", 500
