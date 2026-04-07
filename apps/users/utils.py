import random
import datetime
from django.utils import timezone
from .models import OTPRequest

def generate_otp(phone_number):
    """
    Generates a 4-digit OTP, saves it to DB, and sends it (Simulated).
    """
    # 1. Generate a random 4-digit number
    # using strings ensures we keep leading zeros if any (e.g. '0123')
    otp_code = "{:04d}".format(random.randint(0, 9999))
    
    # 2. Save to Database
    OTPRequest.objects.create(
        phone_number=phone_number,
        otp_code=otp_code,
        created_at=timezone.now()
    )
    
    # 3. Send SMS (Simulated for Development)
    # In production, you would call Twilio/AWS SNS here.
    print(f"\n" + "="*50)
    print(f" [SMS GATEWAY SIMULATION]")
    print(f" To:   {phone_number}")
    print(f" OTP:  {otp_code}")
    print(f"="*50 + "\n")
    
    return otp_code

def verify_otp_logic(phone_number, entered_otp):
    """
    Checks if the entered OTP is valid for the phone number.
    Returns True if valid, False otherwise.
    """
    try:
        # 1. Get the most recent OTP for this phone number
        # We look for records created in the last 5 minutes only
        five_mins_ago = timezone.now() - datetime.timedelta(minutes=5)
        
        otp_record = OTPRequest.objects.filter(
            phone_number=phone_number,
            created_at__gte=five_mins_ago,
            is_verified=False # Only check unverified ones
        ).latest('created_at')
        
        # 2. Check if codes match
        if otp_record.otp_code == entered_otp:
            # 3. Mark as verified so it can't be reused
            otp_record.is_verified = True
            otp_record.save()
            return True
        
        return False

    except OTPRequest.DoesNotExist:
        # No OTP found (or it expired/already used)
        return False