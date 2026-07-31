import os
import smtplib
import random
from email.message import EmailMessage
import functions_framework

# Pre-written library of high-quality routines matching the exact requirements
ROUTINES = [
    """You are a fitness coach. Create a unique daily bodyweight routine.
Requirements:
- 5-minute warm-up: Jump rope (3 mins), arm circles (1 min), high knees (1 min).
- HIIT Workout (40s work, 20s rest - 4 rounds of 5 exercises = 20 mins):
  1. Burpees
  2. Jumping Lunges
  3. Mountain Climbers
  4. Push-ups
  5. Plank Jacks
- Muscle Groups Engaged: Full body, heavily targeting chest, quads, core, and shoulders.
- Estimated Calorie Burn (90kg+ man): ~320-380 kcal.
""",
    """You are a fitness coach. Create a unique daily bodyweight routine.
Requirements:
- 5-minute warm-up: Light jogging in place (3 mins), torso twists (1 min), jumping jacks (1 min).
- Alternative Option: Follow this workout, or alternatively go for a 30-minute run.
- HIIT Workout (40s work, 20s rest - 4 rounds of 5 exercises = 20 mins):
  1. Squat Jumps
  2. Bicycle Crunches
  3. Tricep Dips (on chair)
  4. High Knees
  5. Russian Twists
- Muscle Groups Engaged: Lower body, abdominals, triceps, and cardiovascular system.
- Estimated Calorie Burn (90kg+ man): ~300-350 kcal.
""",
    """You are a fitness coach. Create a unique daily bodyweight routine.
Requirements:
- 5-minute warm-up: Jump rope (3 mins), butt kicks (1 min), side lunges (1 min).
- HIIT Workout (40s work, 20s rest - 4 rounds of 5 exercises = 20 mins):
  1. Tuck Jumps
  2. Spiderman Push-ups
  3. Reverse Lunges
  4. Plank with Shoulder Taps
  5. Speed Skaters
- Muscle Groups Engaged: Glutes, hamstrings, chest, core, and shoulders.
- Estimated Calorie Burn (90kg+ man): ~330-390 kcal.
""",
    """You are a fitness coach. Create a unique daily bodyweight routine.
Requirements:
- 5-minute warm-up: Jumping jacks (3 mins), hip rotations (1 min), arm cross-overs (1 min).
- Alternative Option: Follow this workout, or alternatively go for a 30-minute run.
- HIIT Workout (40s work, 20s rest - 4 rounds of 5 exercises = 20 mins):
  1. Broad Jumps
  2. Diamond Push-ups
  3. V-Ups
  4. Alternating Side Lunges
  5. Burpees without push-up
- Muscle Groups Engaged: Explosive leg power, inner chest, triceps, and upper/lower core.
- Estimated Calorie Burn (90kg+ man): ~310-360 kcal.
""",
    """You are a fitness coach. Create a unique daily bodyweight routine.
Requirements:
- 5-minute warm-up: Shadow boxing (3 mins), dynamic leg swings (1 min), high knees (1 min).
- HIIT Workout (40s work, 20s rest - 4 rounds of 5 exercises = 20 mins):
  1. Bear Crawls (forward and back)
  2. Pistol Squat Progressions (alternating legs)
  3. Hand-release Push-ups
  4. Hollow Body Hold (40s)
  5. Frog Jumps
- Muscle Groups Engaged: Deep core stabilization, chest, quads, calves, and shoulders.
- Estimated Calorie Burn (90kg+ man): ~340-400 kcal.
"""
]

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
        # Randomly select a routine from our offline library
        routine = random.choice(ROUTINES)
        
        email_status = send_email(routine)
        return f"Routine generated. {email_status}", 200
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error generating routine: {e}", 500
