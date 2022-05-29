import  configparser
import yaml

def hostIni() -> str:
    config = configparser.ConfigParser(allow_no_value=True)  # 允许存放空值 默认是键值对存放
    config['master'], config['client'], config['server:children'], config['server:vars'], config['deploy_ip'], config[
        'deploy_client'] = {}, {}, {}, {}, {}, {}
    masterList, clientList, A_record = [], [], []
    config.set('server:children', 'master')
    config.set('server:children', 'client')
    with open('config/yaml/config.yaml', mode='r') as r:
        hostData = yaml.safe_load(r)
    # 如果不配置第二次就无法读取到之前的self.deploy_ip因为可能上面Success.log的生成跳过了步骤
    for data in hostData['hosts']:  # 要先生成deployip
        if hostData['hosts'][hostData['hosts'].index(data)]['deploy'] == True:
            deploy_ip = hostData['hosts'][hostData['hosts'].index(data)]['last_address']
    config.set('server:vars', 'deployIp', deploy_ip)
    config.set('deploy_ip', deploy_ip)
    config.set('server:vars', 'namespace', hostData['namespace'])
    config.set('server:vars', 'ingressDomain', hostData['ingressDomain'])
    config.set('server:vars', 'clusterName', hostData['clusterName'])
    for host in hostData['hosts']:
        config.set('server:vars', 'user', host['username'])
        A_record.append((host['hostname'], host['last_address'], host['password']))
        user = host['username']
        if host['master'] == True:
            config.set('master', host['last_address'])
            masterList.append((host['hostname'], host['last_address']))
            if deploy_ip != host['last_address']:
                config.set('deploy_client', host['last_address'])
        else:
            config.set('client', host['last_address'])
            clientList.append((host['hostname'], host['last_address']))

    config.set('server:vars', 'master', str(masterList))
    config.set('server:vars', 'client', str(clientList))
    config.set('server:vars', 'dns_A_record', str(A_record))
    config.set('server:vars', 'domain', 'uisee')

    with open('mods/ansible/config/host.ini', mode='w') as r:
        config.write(r)
    return user

if __name__ == '__main__':
    hostIni()