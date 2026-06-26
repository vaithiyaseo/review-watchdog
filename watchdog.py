import requests
import smtplib
from email.message import EmailMessage
import os
import sys

# 1. Pull secure keys from GitHub environment memory
SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_PASS = os.environ.get('GMAIL_PASS')

if not all([SERPAPI_KEY, GMAIL_USER, GMAIL_PASS]):
    print("Error: Missing system secrets configuration.")
    sys.exit(1)

# 2. Assign the target profile and destination email
# Replace the string below with the actual Place ID you found earlier
PLACE_ID = "ChIJ0dVrKADpBjsRbOP6XyyCSYM" 
OWNER_EMAIL = "vaithiyanathanmuneeswaran@gmail.com"  # Put your email here for testing

# 3. Connect to SerpApi and fetch the freshest reviews
url = f"https://serpapi.com/search.json?engine=google_maps_reviews&place_id={PLACE_ID}&sort_by=newestFirst&api_key={SERPAPI_KEY}"

try:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"API Connection Failure: {e}")
    sys.exit(1)

# 4. Filter the top 3 newest reviews for poor ratings (3 stars or lower)
reviews = data.get('reviews', [])[:3]
bad_reviews = [r for r in reviews if r.get('rating', 5) <= 3]

# --- ADD THESE TWO LINES FOR TESTING ---
fake_test_review = {"rating": 1, "user": {"name": "Test Account"}, "snippet": "This is a fake test review to verify the automation engine."}
bad_reviews.append(fake_test_review)
# --------------------------------------

# 5. Execute email transfer if issues are found
if bad_reviews:
    msg = EmailMessage()
    msg['Subject'] = "🚨 URGENT: Low Review Alert on Google Maps"
    msg['From'] = GMAIL_USER
    msg['To'] = OWNER_EMAIL
    
    body = "Alert! Our watchdog system detected a low-rating review on your profile:\n\n"
    for item in bad_reviews:
        body += f"⭐ Rating: {item.get('rating')} Stars\n"
        body += f"👤 User: {item.get('user', {}).get('name', 'Anonymous')}\n"
        body += f"💬 Review: {item.get('snippet', 'No written text provided.')}\n"
        body += f"--------------------------------------------------\n\n"
    body += "Please log into your Google Business Profile and address this immediately."
    
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print("Negative review discovered. Alert email sent successfully.")
    except Exception as smtp_err:
        print(f"Email delivery error: {smtp_err}")
else:
    print("Run completed: No negative reviews found in the latest check.")
