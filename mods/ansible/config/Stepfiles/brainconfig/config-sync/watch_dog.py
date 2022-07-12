import requests
import sys
import threading
import time

m_lock = threading.Lock()
thread_lst = []
services = {
    'kong': f'https://{sys.argv[1]}:32444/consumers',
    'minio': f'http://{sys.argv[1]}:30003/minio/login',
    'nacos': f'http://{sys.argv[1]}:31205/nacos/',
    'cloud-emqx': f'http://{sys.argv[1]}:32290/',
    'emqx': f'http://{sys.argv[1]}:32291/',
    # 'console':f'https://{sys.argv[2]}/api/console/system/security/login'
}
service_ready = []
service_status = {'kong': "NotReady", 'minio': "NotReady", 'nacos': "NotReady", 'cloud-emqx': "NotReady",
                  'emqx': "NotReady"}
# service_status = {'kong': "NotReady", 'minio': "NotReady", 'nacos': "NotReady", 'cloud-emqx': "NotReady",
#                   'emqx': "NotReady",'console':'NotReady'}

def kong(baseurl, name):
    # global service_status
    while True:
        try:
            #        if name=='console':
            #           s = requests.Session()

            #          adminAccount = {'username': 'admin',
            #                     'password': 'uisee@future'}
            #         status_num=s.post(url=baseurl, data=adminAccount, verify=False).status_code

            if name == 'minio':
                head = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
                status_num = requests.get(url=baseurl, verify=False, timeout=10, headers=head).status_code

            else:
                status_num = requests.get(url=baseurl, verify=False, timeout=10).status_code

        except  Exception as e:
            status_num = 500
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
    print(f'{service_status}\r', end='', flush=True)
    if len(service_ready) == 5:
        break

print('============================================================================================')
print('Ready! Import config for Kong,minio,nacos,cloud-emqx,emqx ')
time.sleep(2)
