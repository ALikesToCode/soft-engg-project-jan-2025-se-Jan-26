from datetime import datetime

exp_timestamp = 1740849674  # Replace with actual 'exp' value from decoded JWT
exp_time = datetime.utcfromtimestamp(exp_timestamp)
current_time = datetime.utcnow()

if current_time > exp_time:
    print("Token is expired")
else:
    print("Token is still valid")
