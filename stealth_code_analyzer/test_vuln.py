# GAHENAX SAST TEST FILE
import os

def vulnerable_function():
    user_input = os.environ.get("USER_DATA") # SOURCE
    
    # Vulnerabilidad 1: RCE
    os.system(user_input) # SINK
    
    # Vulnerabilidad 2: SQLi (Simulada)
    query = "SELECT * FROM users WHERE id = " + user_input
    # db.execute(query) # Simulando sink
    
if __name__ == "__main__":
    vulnerable_function()
