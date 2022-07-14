import requests
import sys
import json
from mods.logs.log import service_logger
header={
"Authorization": "Basic YWRtaW46cHVibGlj"
}
requests.DEFAULT_RETRIES = 5  # 增加重试连接次数
# s = requests.session()
# s.keep_alive = False  # 关闭多余连接
def upload():

    with open(f'{sys.argv[2]}/emqx/cloud-emqx-jiashan-prod.json') as f:
        cloud=f.read()
    with open(f'{sys.argv[2]}/emqx/emqx-jiashan-prod.json') as f:
        emqx=f.read()

    cloud_data={
            'filename':'cloud-emqx-jiashan-prod.json',
            'file':cloud
            }
    emqx_data={
    'filename':'emqx-jiashan-prod.json',
            'file':emqx
            }
    url=f'http://{sys.argv[1]}:32290/api/v4/data/file'

    cloud_result=requests.post(url,headers=header,data=json.dumps(cloud_data))
    url=f'http://{sys.argv[1]}:32291/api/v4/data/file'
    emqx_result=requests.post(url,headers=header,data=json.dumps(emqx_data))
    try:
       return  cloud_result.json()['data']['node'],emqx_result.json()['data']['node']
    except Exception as e:
       service_logger.info('Data was error  please check the script')
       raise
def import_file(cloud_result,emqx_result):
    cloud_import_data={
            'filename':'cloud-emqx-jiashan-prod.json',
            'node':cloud_result
            }
    emqx_import_data={
    'filename':'emqx-jiashan-prod.json',
        'node':emqx_result

            }
    url=f'http://{sys.argv[1]}:32290/api/v4/data/import'
    import_result=requests.post(url,headers=header,data=json.dumps(cloud_import_data))
    service_logger.info(import_result.json())

    url=f'http://{sys.argv[1]}:32291/api/v4/data/import'
    import_result=requests.post(url,headers=header,data=json.dumps(emqx_import_data))
    service_logger.info(import_result.json())

if __name__ == '__main__':
    cloud_result, emqx_result= upload()
    import_file(cloud_result,emqx_result)
