import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IjIyZjEwMDExMjhAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsInJvbGUiOiJzdHVkZW50IiwiZXhwIjoxNzQwODQ5Njc0fQ.aN8NP8-DwKPBj5kQw6jgToYHz1-Lc_dZIMXvugT6Sis"  # Replace with your actual token
decoded = jwt.decode(token, options={"verify_signature": False})  # No signature verification
print(decoded)
