import requests
import sys
import threading
import time

m_lock = threading.Lock()
thread_lst = []
services = {
     'console':f'https://{sys.argv[2]}/api/console/system/security/login'
}

head={
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }
adminAccount = {'username': 'admin','password': 'uisee@future'}
service_ready = []
service_status = {'console':'NotReady'}
requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接
def kong(baseurl, name):

    while True:
        try:
                status_num = s.post(headers=head,url=baseurl, verify=False, timeout=10,data=adminAccount).status_code
        except  Exception as e:
            print(e)
            status_num = 500
        print(status_num)
        if status_num == 200:
            with m_lock:
                service_ready.append(True)
                service_status[name] = 'Ready'
            break
        time.sleep(3)
for key, value in services.items():
    th = threading.Thread(target=kong, args=(value, key))
    th.daemon = True
    th.start()

while 1:
    time.sleep(0.5)
    print(f'Console ------- {service_status["console"]}\r', end='', flush=True)
    if len(service_ready) == 1:
        break
print('============================================================================================')
print('Ready! Import config for Console ')
time.sleep(2)
