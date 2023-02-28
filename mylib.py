from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoSuchElementException
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from time import sleep
from datetime import datetime
import argparse
import getpass

def myfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, help="基本延遲時間[6.00]", default=6.00)
    parser.add_argument("--enlarge", type=float, help="延遲增長倍率[1.43]", default=1.43)
    parser.add_argument("--deflate", type=float, help="延遲縮短倍率[0.96]", default=0.96)
    parser.add_argument("--headless", help="無視窗模式", action='store_true')
    parser.add_argument('--no-headless', help="關閉無視窗模式", dest='headless', action='store_false')
    parser.set_defaults(headless=True)
    args = parser.parse_args()

    delay = args.delay

    options = webdriver.EdgeOptions()
    options.add_argument('--disable-web-security --disable-dev-shm-usage')

    if args.headless == True:
        options.add_argument('--headless --disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Edge(options=options)
    driver.get('https://aais1.nkust.edu.tw/selcrs_dp')

    # 登入頁面
    while True:
        UserAccount = input("Account: ")
        Password = getpass.getpass()

        account = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'UserAccount')))
        account.send_keys(UserAccount)
        password = driver.find_element(By.ID, 'Password')
        password.send_keys(Password)

        login = driver.find_element(By.ID, 'Login')
        login.click()
        try:
            sleep(0.2)
            toast = driver.find_element(By.CSS_SELECTOR, 'div#toast-container div.toast div.toast-message')
            if toast.text == "密碼錯誤，登入失敗！":
                print("Login Failed!")
        except NoSuchElementException:
            print("Login Success!")
            break

    # 輸入課程代碼
    Crsno_List = input("Courses: ").split()

    # 加退選畫面 Adding Courses
    wait = WebDriverWait(driver, 8)
    courses = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.nav-pills li:first-child')))
    x_offset = courses.location['x'] + courses.size['width'] + 20
    y_offset = courses.location['y']
    courses.click()

    adding = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.menu-open ul li:first-child')))
    adding.click()

    action = ActionChains(driver)
    action.move_by_offset(x_offset, y_offset)
    action.click()
    action.perform()
    print(f"[INFO:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Start adding loop...")

    while Crsno_List:
        for Crsno in Crsno_List.copy():
            course_numero = wait.until(EC.presence_of_element_located((By.ID, 'scr_selcode')))
            course_numero.send_keys(Crsno)

            while True:
                try:
                    search = driver.find_element(By.ID, "courseSearch")
                except UnexpectedAlertPresentException:
                    driver.switch_to().alert().accept()
                else:
                    search.click()
                    break
                finally:
                    sleep(0.2)
            
            while True:
                while True:
                    try:
                        add_it = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.text-center button.btn_addcrs")))
                    except UnexpectedAlertPresentException:
                        driver.switch_to().alert().accept()
                    else:
                        sleep(delay)
                        try:
                            print(f"[INFO:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Adding Crsno:", Crsno)
                            add_it.click()
                            break
                        except (StaleElementReferenceException, TimeoutException):
                            print(f"[ERROR:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Adding Failed! Retrying...")
                    finally:
                        sleep(0.2)
                
                crs_name = add_it.find_element(By.XPATH, '../..//a[@class="myLink"]').text
                print(f"[INFO:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Added:", crs_name, end=' ')
                
                toast = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#toast-container div.toast div.toast-message')))
                if '加選間隔太短' in toast.text:
                    delay = round(delay * args.enlarge, 3)
                    print(f'-> too fast, changing delay to {delay:.2f} s')
                elif '限修人數已額滿!' in toast.text:
                    print("-> Fulled")
                    delay = round(delay * args.deflate, 3)
                    break
                elif "衝堂，不可選!" in toast.text or "違反重複同課程限修(課號)!" in toast.text:
                    print("-> Failed ", '->', toast.text)
                    Crsno_List.remove(Crsno)
                    break
                elif "加入選課完成！" in toast.text:
                    print("-> Success")
                    Crsno_List.remove(Crsno)
                    break
                else:
                    print("-> Unkdatetime.nown action:\n$$$$$\n", toast.text, '\n$$$$$')
                    Crsno_List.remove(Crsno)
                    break

    print(f"[INFO:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]Done!")
    driver.quit()

    return "Done!"
