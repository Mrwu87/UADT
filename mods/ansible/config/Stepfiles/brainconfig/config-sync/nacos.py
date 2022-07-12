import requests
import sys
from mods.logs.log import service_logger

requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
s = requests.session()
s.keep_alive = False  # 关闭多余连接
createNamespace='http://%s/nacos/v1/console/namespaces'  % (sys.argv[1])
dataer={'customNamespaceId': f'{sys.argv[3]}','namespaceName':f'{sys.argv[3]}'}
head={
'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'}

r = s.post(url=createNamespace, data=dataer,headers=head,timeout=10)

try:
    service_logger.info(r.json())
except:
    service_logger.info('Fail: Create namespace was failed')
restoreUrl = 'http://%s/nacos/v1/cs/configs'  % (sys.argv[1])
with open(f'{sys.argv[2]}/nacos/config.txt','r') as f:
    config_content=f.read()
with open(f'{sys.argv[2]}/nacos/policy.txt','r') as f:
   policy_content=f.read()
config_payload={
    'dataId': 'config_json',
    'group': 'cloud_nome',
    'tenant': 'compass-ha',
    'content': config_content
}
policy_payload={
    'dataId': 'policy_rego',
    'group': 'cloud_nome',
    'tenant': 'compass-ha',
    'content': policy_content
}

# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'


result = s.post(url=restoreUrl,headers=head,data=config_payload,timeout=10)
service_logger.info(result.json())

result = s.post(url=restoreUrl,headers=head,data=policy_payload,timeout=10)
service_logger.info(result.json())
