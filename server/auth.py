import sqlite3
import os
import bcrypt
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database1.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def register (User, Password):
    nid = gen_user_id()
    validate_password(Password)
    validate_username(User)
    hashed_password = hash_password(Password)
    cursor.execute("INSERT INTO userinfo (pseudo,password,balance,id) VALUES (?,?,?,?)",(User,hashed_password,0,nid))
    conn.commit()
    
def gen_user_id():
    cursor.execute("SELECT MAX(id) FROM userinfo")
    result = cursor.fetchone()
    if result[0] is None:
        nid = 1
    else:
        nid = result[0]+1
    return nid

def validate_password(password):
    if len(password)<6:
        raise ValueError("Le mot de passe doit faire au moins six caractères")
    elif len(password)>32:
        raise ValueError("Le mot de passe doit faire moins de trente deux caractères")
    else:
        return True

def validate_username(User):
    if len(User)<3:
        raise ValueError("Le pseudo doit faire au moins trois caractères")
    elif len(User)>25:
        raise ValueError("Le pseudo doit faire moins de vingt cinq caractères")
    else:
        return True

def user_exists(User):
    cursor.execute("SELECT * FROM userinfo WHERE pseudo = ?", (User))
    result = cursor.fetchone()
    if result is None:
        return False
    else:
        return True

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def login(User, Password):
    cursor.execute("SELECT * FROM userinfo WHERE pseudo = ? AND password = ?", (User, check_password(Password)))
    result = cursor.fetchone()
    if result is None:
        return False
    else:
        return True

def add_balance(User, Amount):
    cursor.execute("UPDATE userinfo SET balance = balance + ? WHERE pseudo = ?", (Amount, User))
    conn.commit()