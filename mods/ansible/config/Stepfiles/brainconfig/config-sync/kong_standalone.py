'''
Date: 2021-06-02 10:29:50
LastEditors: yuxuan.liu@uisee.com
LastEditTime: 2021-11-10 17:20:24
FilePath: /data/config-sync/kong_standalone.py
Description: 
'''
from posix import listdir
import requests
import json
from mods.logs.log import service_logger
import sys
from jinja2 import Environment, FileSystemLoader
import os
import requests
from ruamel import yaml
import json
import requests
import urllib3
urllib3.disable_warnings()


                
def render_template(template, value_file, output=None):

    valuefile = open(value_file, 'rt')
    value = valuefile.read()
    yfile = yaml.safe_load(value)

    basepath = os.path.dirname(template)
    filename = os.path.basename(template)

    templateLoader = FileSystemLoader(searchpath=basepath)
    env = Environment(loader=templateLoader)
    tmpl = env.get_template(filename)
    result = tmpl.render(yfile)
    with open(output, "w") as fh:
        fh.write(result)


class KongaImporter:
    def __init__(self, clusterKong,namespace,domain=None,op_domain=None) -> None:
        super().__init__()
        self.clusterKong = clusterKong.rstrip('/')
        self.namespace = namespace
        self.domain = domain
        self.op_domain = op_domain
        self.session = requests.session()
        self.value_file = f'{sys.argv[4]}/kong_configs/value.yaml'
        self.baseDir = f'{sys.argv[4]}/kong_configs/'

        consumerUrl = self.clusterKong + '/consumers/anonymous'
        consumerCreate = self.clusterKong + '/consumers/'
        try:
            service_logger.info(self.session.get(
                url=consumerUrl, verify=False).json()['id'])
        except Exception as e:
            createUsername={
                'username':'anonymous'
            }
            service_logger.info(self.session.post(url=consumerCreate, verify=False,data=createUsername).json())

        KONG_ANONYMOUS = self.session.get(
            url=consumerUrl, verify=False).json()['id']
        valueDic = {}
        valueDic['KONG_ANONYMOUS'] = KONG_ANONYMOUS
        valueDic['NAMESPACE'] = self.namespace
        if self.domain != None:
            valueDic['DOMAIN'] = self.domain
        if self.op_domain != None:
            valueDic['OP_DOMAIN'] = self.op_domain


        output = open((self.value_file), mode='wt')
        yaml.round_trip_dump(
            valueDic, output, default_flow_style=False, allow_unicode=True)
        # output.close()

    def Render(self):
        serviceTmpl = listdir(f'{sys.argv[4]}/kong_configs/tmpl/service')
        routeTmpl = listdir(f'{sys.argv[4]}/kong_configs/tmpl/route')
        pluginTmpl = listdir(f'{sys.argv[4]}/kong_configs/tmpl/plugin')

        for svc in serviceTmpl:
            filePath =('%s/tmpl/service/%s') % (self.baseDir,svc)
            render_template(template=filePath,value_file=self.value_file,output=f'{sys.argv[4]}/kong_configs/output/service/'+svc)

        for rot in routeTmpl:
            filePath =('%s/tmpl/route/%s') % (self.baseDir,rot)
            render_template(template=filePath,value_file=self.value_file,output=f'{sys.argv[4]}/kong_configs/output/route/'+rot)

        for plg in pluginTmpl:
            filePath =('%s/tmpl/plugin/%s') % (self.baseDir,plg)
            render_template(template=filePath,value_file=self.value_file,output=f'{sys.argv[4]}/kong_configs/output/plugin/'+plg)

    def Import(self):
        serviceOutput = listdir(f'{sys.argv[4]}/kong_configs/output/service')
        routeOutput = listdir(f'{sys.argv[4]}/kong_configs/output/route')
        pluginOutput = listdir(f'{sys.argv[4]}/kong_configs/output/plugin')

        for svc in serviceOutput:
            filePath =('%soutput/service/%s') % (self.baseDir,svc)
            jsonData = json.load(
                open(filePath, mode='rt', encoding='utf-8'))
            svcUrl = self.clusterKong + '/services/' +  jsonData['name']
            # service_logger.info('[KONG] PostURL: %s' % svcUrl)
            service_logger.info('PUT URL: %s' % svcUrl)
            result = self.session.put(
                url=svcUrl, json=jsonData, verify=False)
            if result.status_code == 409:
                Desc = 'Duplicate item.'
            elif result.status_code == 200:
                Desc = 'Updated.'
            elif result.status_code == 201:
                Desc = 'Created.'
            else:
                Desc = result.text
            service_logger.info('[KONG] KONGA API > Service : KongRespone: %s, Desc: %s , svcName:    %s, Host: %s' % (
                result.status_code, Desc,jsonData['name'], jsonData['host']))


        for rot in routeOutput:
            filePath =('%soutput/route/%s') % (self.baseDir,rot)
            jsonData = json.load(
                open(filePath, mode='rt', encoding='utf-8'))
            routeUrl = self.clusterKong + '/routes/' + jsonData['name']
            result = self.session.put(url=routeUrl, json=jsonData, verify=False)
            attachTo = jsonData['service']['name']
            if result.status_code == 409:
                Desc = 'Duplicate item.'
            elif result.status_code == 200:
                Desc = 'Updated.'
            elif result.status_code == 201:
                Desc = 'Created.'
            else:
                Desc = result.text
            service_logger.info('[KONG] KONGA API > Route   :KongRespone: %s, Desc: %s , routeName:  %s, Attach to svc: %s' % (
                result.status_code, Desc,jsonData['name'], attachTo))


        for plg in pluginOutput:

            filePath =('%soutput/plugin/%s') % (self.baseDir,plg)
            jsonData = json.load(
                open(filePath, mode='rt', encoding='utf-8'))
            for item in jsonData:
                if item['route'] != None:
                    pluginType = 'routes'
                    attachTo = item['route']['name']
                elif item['service'] != None:
                    pluginType = 'services'
                    attachTo = item['service']['name']

                pluginUrl = self.clusterKong + '/plugins'
                result = self.session.post(url=pluginUrl, json=item, verify=False)

                getUrl = '%s/%s/%s/plugins' % (self.clusterKong,pluginType,attachTo)
                # pluginId = self.session.get(url=getUrl,verify=False).json()['data'][0]['id']
                for i in self.session.get(url=getUrl,verify=False).json()['data']:
                    if item['name'] == i['name']:
                        pluginId = i['id']
                putUrl = '%s/plugins/%s' % (self.clusterKong,pluginId)
                putResult = self.session.put(url=putUrl, json=item, verify=False)

                # service_logger.info('[KONG] DUMP putURL: %s putJSON: %s' % (putUrl,item))

                if result.status_code == 409:
                    Desc = 'Duplicate item.'
                elif result.status_code == 200:
                    Desc = 'Updated.'
                elif result.status_code == 201:
                    Desc = 'Created.'
                else:
                    Desc = result.text
                service_logger.info('[KONG] KONGA API > plugin: KongRespone: %s, Desc: %s, pluginName: %s, Attach to %s: %s ' % (
                    result.status_code, Desc,item['name'], pluginType, attachTo, ))

                if putResult.status_code == 409:
                    Desc = 'Duplicate item.'
                elif putResult.status_code == 200:
                    Desc = 'Updated.'
                elif putResult.status_code == 201:
                    Desc = 'Created.'
                else:
                    Desc = putResult.text
                service_logger.info('[KONG] KONGA API > plugin: KongRespone: %s, Desc: %s, pluginName: %s, Patch to %s: %s' % (
                    putResult.status_code, Desc, item['name'], pluginType, attachTo))




# try:
#     clusterKong= input('Kong Admin url [e.g: https://kong.uisee.com:30001]: ')
#     domain= input('Domain [e.g: console.uisee.com]: ')
#     op_domain= input('Operator domain [e.g: console.uisee.com]: ')
#     namespace= input('namespace: ')
#     print('\nPlease confirm your config:\nclusterKong: %s\ndomain: %s\nop_domain: %s\nnamespace: %s\n' %(clusterKong,domain,op_domain,namespace))
#     while True:
#         confirm = input('Confirm: [N/y]: ')
#         if confirm.strip(' ') == 'y':
#             kongimporter = KongaImporter(clusterKong=clusterKong,domain=domain,op_domain=op_domain,namespace=namespace)
#             kongimporter.Render()
#             kongimporter.Import()
#             service_logger.info('Kong import success')
#             break
#         elif confirm.strip(' ') == "":
#             continue
#         else:
#             print('Bye.')
#             break
# except KeyboardInterrupt:
#     print('\n"Ctrl+c" catched, Bye.')

if __name__ == '__main__':
    result=False
    #32444
    clusterKong= sys.argv[1]
    domain= sys.argv[2]
    op_domain= None
    namespace= sys.argv[3]
    kongimporter = KongaImporter(clusterKong=clusterKong,domain=domain,op_domain=op_domain,namespace=namespace)
    kongimporter.Render()
    kongimporter.Import()
    result=True
