import urllib.request
import json
import urllib.error
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Hash import SHA256
import uuid

url_base = "http://127.0.0.1:8000"

donnees_bidon = {
    "message": json.dumps({"test": "valeur"}),
    "signature": "mauvaise_signature"
}
body = json.dumps(donnees_bidon).encode("utf-8")

print("sans token")
try:
    auth_sans_token = urllib.request.Request(f"{url_base}/create-auction", data=body, headers={'Content-Type': 'application/json'})
    reponse = urllib.request.urlopen(auth_sans_token)
except urllib.error.HTTPError as e:
    print(f"Erreur reçue : {e.code}")
    print(f"Message : {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Erreur : {e}")

print("\n mauvais token")
try:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mauvais.token.bidon'
    }
    auth_mauvais_token = urllib.request.Request(f"{url_base}/create-auction", data=body, headers=headers)
    reponse = urllib.request.urlopen(auth_mauvais_token)
except urllib.error.HTTPError as e:
    print(f"Erreur reçue : {e.code}")
    print(f"Message : {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Erreur : {e}")

print("\n mauvaise signature")
try:
    donnees_signature_fausse = {
        "message": json.dumps({"title": "Faux", "price": 0, "timestamp": 0, "description": "test"}),
        "signature": "signature_invalide_mais_presente"
    }
    body_sig = json.dumps(donnees_signature_fausse).encode("utf-8")
    
    headers_sig = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-IDcSemACt8x4iT5e35exGgeks'
    }
    req_sig = urllib.request.Request(f"{url_base}/create-auction", data=body_sig, headers=headers_sig)
    reponse = urllib.request.urlopen(req_sig)
except urllib.error.HTTPError as e:
    print(f"Erreur reçue : {e.code}")
    print(f"Message : {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Erreur : {e}")

def rsa_encrypt(message, publicKey):
    m = bytes_to_long(message.encode("utf-8"))
    if m >= publicKey["n"]:
        return None
    c = pow(m, publicKey["e"], publicKey["n"])
    return str(c)

def rsa_sign(message, privateKey):
    hash = SHA256.new(message.encode("utf-8"))
    m = bytes_to_long(hash.hexdigest().encode("utf-8"))
    signature = pow(m, privateKey["d"], privateKey["n"])
    return signature

def generate_keys():
    key = RSA.generate(2048)
    private_key = {"d": key.d, "n": key.n, "e": key.e}
    public_key = {"e": key.e, "n": key.n}
    return key.e, key.n, private_key

def get_server_key():
    req = urllib.request.Request(f"{url_base}/auth/public-key", headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        msg = json.loads(data['message'])
        return {"e": int(msg['e']), "n": int(msg['n'])}

def register_and_login(username, password):
    server_key = get_server_key()
    pk_e, pk_n, client_priv_key = generate_keys()
    reg_data = {
        "username": rsa_encrypt(username, server_key),
        "password": rsa_encrypt(password, server_key),
        "public_key_e": str(int(pk_e)),
        "public_key_n": str(int(pk_n))
    }
    req_reg = urllib.request.Request(f"{url_base}/auth/register", data=json.dumps(reg_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req_reg) as response:
        response.read()

    login_data = {
        "username": rsa_encrypt(username, server_key),
        "password": rsa_encrypt(password, server_key),
        "public_key_e": str(int(pk_e)),
        "public_key_n": str(int(pk_n))
    }
    req_login = urllib.request.Request(f"{url_base}/auth/login", data=json.dumps(login_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    token = None
    with urllib.request.urlopen(req_login) as response:
        resp_json = json.loads(response.read().decode('utf-8'))
        inner_msg = json.loads(resp_json['message'])
        token = inner_msg['access_token']
    return token, client_priv_key

print("\n token valide mais signature falsifiée")
try:
    rnd_user = f"hacker_{uuid.uuid4().hex[:8]}"
    rnd_pass = "password123"
    token, client_priv_key = register_and_login(rnd_user, rnd_pass)

    payload_dict = {
        "title": "Hacked Auction",
        "description": "Should not exist",
        "price": 100,
        "timestamp": 1234567890
    }
    message_str = json.dumps(payload_dict, separators=(",", ":"), sort_keys=True)
    fake_message_for_sig = json.dumps({"title": "Original"}, separators=(",", ":"), sort_keys=True)
    fake_signature = rsa_sign(fake_message_for_sig, client_priv_key)
    final_data = {
        "message": message_str,
        "signature": str(fake_signature)
    }
    body_integrity = json.dumps(final_data).encode("utf-8")
    headers_integrity = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    req_integrity = urllib.request.Request(f"{url_base}/create-auction", data=body_integrity, headers=headers_integrity)
    reponse = urllib.request.urlopen(req_integrity)
except urllib.error.HTTPError as e:
    print(f"Erreur reçue : {e.code}")
    print(f"Message : {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Erreur : {e}")
