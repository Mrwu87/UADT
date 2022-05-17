import os
import yaml,json
from mods.commands.command import Command
from mods.logs.log import service_logger


class Deployment(Command):
    def logic(self, file, sh, error_message, task_id, *args) -> bool:
        file_pwd=os.getcwd()+'/'+file
        with open('config/yaml/config.yaml', mode='r') as r:
            hostData = yaml.safe_load(r)
        for i in hostData['hosts']:
            if hostData['hosts'].index(i) == 0:
                # self.run_command(f'rm -rf {file}', taskId='rm log', )
                try:
                    os.remove(file_pwd)
                except Exception as e:
                    pass
            if self.run_command(f'bash {sh} {" ".join([str(i[ii]) for ii in args])}',taskId=f'{task_id}', ):  # 传递任意变量进入能解析到sh中
                continue
            else:  # 执行脚本内的错误捕捉输出
                # os.system(exit())
                return False
        if os.path.exists(file) == True:  # 捕捉自定义错误如checkip.sh中自定义的错误内容
            service_logger.info(f'{error_message}')
            return False
        else:
            dir = "/".join([ s for s in  file.split("/")[0:-1]])
            # print(os.getcwd(),dir)
            os.mknod(f'{os.getcwd()}/{dir}/Success.log')
            if f'{dir}/Success.log' == 'mods/services/config/expectcheck/Success.log':  #
                for data in hostData['hosts']:
                    new_address=hostData['hosts'][hostData['hosts'].index(data)]['new_address'].split('/')[0]
                    hostData['hosts'][hostData['hosts'].index(data)]['last_address'] = new_address
                    if hostData['hosts'][hostData['hosts'].index(data)]['deploy'] == True:
                        self.deploy_ip = new_address
                    hostData['hosts'][hostData['hosts'].index(data)]['deploy_ip'] = self.deploy_ip
                with open('config/yaml/config.yaml', mode='w') as file:
                   file.write(yaml.dump(hostData, sort_keys=False))  # sort_keys保持原来的文件field顺序

            return True
    def loop(self,file, action, sh, error_message, task_id, *args):
        while True:
            if action(file, sh, error_message, task_id, *args) == True:
                # service_logger.info(r'Success！')
                break
            # retry = input('是否重试？ y/n')
            # if retry == 'y':
            #     continue
            # else:
            #     os.system(exit())

    def Start(self):
        from mods.services.npy import Npy
        App = Npy()
        App.run()
        with open('config/yaml/stream.yaml', 'r') as f:
            stream = yaml.safe_load(f)
        for i in stream['initasks']:
            dir = "/".join([ s for s in  i['log'].split("/")[0:-1]])
            # print(dir)
            # {key: index for index, key in enumerate(data)}.get('a')  #字典找下标
            count=stream['initasks'].index(i)+1
            App.vc.set_value(count)
            App.F.display()
            #App.F.edit()
            if os.path.exists(f'{dir}/Success.log') == False:
                self.loop(i['log'], self.logic, i['sh'], i['error_message'], i['task_id'], *i['vars'])
            else:
                continue
        return App,count

