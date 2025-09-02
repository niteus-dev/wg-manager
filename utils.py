import subprocess

def run_command(command, input_data=None):
    try:
        result = subprocess.run(command, input=input_data, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return None

def generate_keypair():
    private_key = run_command(["wg", "genkey"])
    public_key = run_command(["wg", "pubkey"], input_data=private_key)
    return private_key, public_key
