# import secrets

# secret_key = secrets.token_hex(32) 
# print(secret_key)


from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
