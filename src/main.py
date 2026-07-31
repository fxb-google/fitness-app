import os
import smtplib
import random
from email.message import EmailMessage
import functions_framework

def get_random_routine() -> str:
    routines = [
        "HIIT Routine 1: 40s work / 20s rest (20 mins)\nWarm-up: 5 mins jumping jacks & high knees.\n- Push-ups (Chest, Triceps, Core)\n- Bodyweight Squats (Quads, Glutes)\n- Mountain Climbers (Core, Shoulders)\n- Lunges (Legs)\n- Plank (Core)\nAlternative: 30-minute run.\nEstimated Calorie Burn: ~300 kcal.",
        "HIIT Routine 2: 40s work / 20s rest (20 mins)\nWarm-up: 5 mins jump rope simulation.\n- Burpees (Full body)\n- Bicycle Crunches (Core, Obliques)\n- Jump Squats (Legs, Cardio)\n- Tricep Dips on chair (Triceps)\n- High Knees (Cardio, Legs)\nAlternative: 30-minute swim.\nEstimated Calorie Burn: ~320 kcal.",
        "HIIT Routine 3: 40s work / 20s rest (20 mins)\nWarm-up: 5 mins light jogging in place.\n- Spiderman Push-ups (Chest, Core)\n- Bulgarian Split Squats (Quads, Glutes)\n- Russian Twists (Core)\n- Bear Crawls (Shoulders, Core)\n- Wall Sit (Quads)\nAlternative: 45-minute brisk walk.\nEstimated Calorie Burn: ~290 kcal.",
        "HIIT Routine 4: 40s work / 20s rest (20 mins)\nWarm-up: 5 mins dynamic stretching.\n- Jumping Lunges (Legs, Cardio)\n- Diamond Push-ups (Triceps, Chest)\n- V-Ups (Core)\n- Skaters (Glutes, Cardio)\n- Plank Jacks (Core, Shoulders)\nAlternative: 30-minute cycling.\nEstimated Calorie Burn: ~310 kcal.",
        "HIIT Routine 5: 40s work / 20s rest (20 mins)\nWarm-up: 5 mins shadow boxing.\n- Tuck Jumps (Cardio, Legs)\n- Pike Push-ups (Shoulders)\n- Flutter Kicks (Lower Core)\n- Reverse Lunges (Glutes, Quads)\n- Superman Holds (Lower Back)\nAlternative: 30-minute rowing.\nEstimated Calorie Burn: ~305 kcal."
    ]
    return random.choice(routines)

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
        routine = get_random_routine()
        email_status = send_email(routine)
        return f"Routine generated. {email_status}", 200
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error generating routine: {e}", 500
