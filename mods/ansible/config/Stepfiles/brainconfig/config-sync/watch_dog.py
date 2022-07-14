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
        service_status[name] = 'Ready'
        #   service_ready.append(True)
        #    service_status[name] = 'Ready'
        from prettytable import PrettyTable
        x = PrettyTable()
        x.field_names = ["Service", "Status"]
        x.add_row(["kong", service_status['kong']])
        x.add_row(["minio", service_status['minio']])
        x.add_row(["nacos", service_status['nacos']])
        x.add_row(["cloud-emqx", service_status['cloud-emqx']])
        x.add_row(["emqx", service_status['emqx']])
        with open(f'/home/{sys.argv[2]}/UADT/mods/logs/config/runtime', 'w') as f:
            f.write(x.get_string() + '\n')

    time.sleep(1)
while 1:
    service_ready = []
    for key, value in services.items():
        kong(value, key)
    [service_ready.append(value) for key, value in service_status.items() if value == 'Ready']
    # print(service_ready)
    if len(service_ready) >= 5:
        break
