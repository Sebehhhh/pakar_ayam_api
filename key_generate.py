import secrets

# Generate a 32-character random string
SECRET_KEY = secrets.token_hex(32)

print(SECRET_KEY)
