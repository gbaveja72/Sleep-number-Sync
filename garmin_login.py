import os
from garminconnect import Garmin

def get_mfa_code():
    return input("Enter your Garmin MFA code: ").strip()

def main():
    print("="*50)
    print(" Garmin Connect Local Authenticator ")
    print("="*50)
    
    email = input("Garmin Email: ").strip()
    password = input("Garmin Password: ").strip()
    
    print("\nAttempting login (you may be prompted for an MFA code)...")
    
    try:
        # Initialize with the prompt_mfa callback
        garmin = Garmin(
            email=email,
            password=password,
            prompt_mfa=get_mfa_code
        )
        garmin.login()
        print("\n✅ Login successful!")
        print("Your authentication tokens have been securely saved to ~/.garminconnect/garmin_tokens.json")
        print("Future automated syncs will use these tokens and bypass the password/MFA prompt completely.")
    except Exception as e:
        print(f"\n❌ Login failed: {e}")

if __name__ == "__main__":
    main()
