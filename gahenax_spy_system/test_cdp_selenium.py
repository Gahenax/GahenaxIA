import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def test_selenium():
    print("Testing Selenium connection to 9222...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Encontrar la tab de FaucetPay Mines
        found = False
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if 'mines' in driver.current_url.lower():
                found = True
                print("Found Mines tab:", driver.current_url)
                break
                
        if not found:
            print("Mines tab not found.")
            driver.quit()
            return
            
        # Intentar extraer info
        bet_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'bet') or contains(@class, 'betButton')]")
        print(f"Number of bet buttons found: {len(bet_btn)}")
        
        grid_btns = driver.find_elements(By.XPATH, "//div[contains(@class, 'style_body__')]//button")
        print(f"Number of grid buttons found: {len(grid_btns)}")
        
        # No cerramos el driver intencionalmente para no cerrar la sesion del usuario
        # driver.quit() no es necesario si solo reconectamos, pero limpiar la instancia es bueno
        # Sin embargo, quit() podria cerrar el navegador si fue el que inicio el chromedriver.
        # Mejor no llamar a quit(), o dejar que el proceso termine.
        print("Success.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_selenium()
