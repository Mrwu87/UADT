import subprocess
import json, yaml
from log import logger
from datetime import datetime, timedelta
from time import sleep
from log import logger
import os
import configparser


class Command():
    def run_command(self, command, taskId, cwd=None, timeout=600):
        try:
            logger.info('[COMMAND] [%s] RUN CMD: [%s], CWD: [%s], TIMEOUT: [%s]' %
                        (taskId, command, cwd, timeout))
            popen = subprocess.Popen(
                command,
                cwd=cwd,
                close_fds=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10000,
                shell=True
            )
            end_time = datetime.now() + timedelta(seconds=timeout)
            while True:
                stdout, stderr = popen.communicate()
                stdout_text = (stdout.decode('utf8')).strip()
                stderr_text = stderr.decode('utf8')
                if popen.poll() is not None:
                    break
                try:
                    print(stdout_text)
                except Exception as e:
                    pass
                # print(stderr_text)
                sleep(0.1)
                if end_time <= datetime.now():
                    popen.kill()
                    logger.critical('[COMMAND] [%s] EXEC TIMEOUT' % (taskId))
                    return False, None, None

            if popen.returncode > 0:
                logger.info('[COMMAND] [%s] FAILED:[%s], CODE:[%s], \nSTDOUT:[\n%s\n]\nSTDERR:[\n%s\n]' % (
                    taskId, command, popen.returncode, stdout_text, stderr_text))

                return False
            else:
                logger.info('[COMMAND] [%s] SUCCESS:[%s], CODE:[%s]' %
                            (taskId, command, popen.returncode))
                return True
        except Exception as e:
            logger.exception('[COMMAND] [%s] EXCEPTION:[%s]:' % (taskId, command))
            return False


class Deployment(Command):
    def logic(self, file, sh, error_message, task_id, *args) -> bool:
        with open('config.yaml', mode='r') as r:
            hostData = yaml.safe_load(r)
        for i in hostData['hosts']:
            if hostData['hosts'].index(i) == 0:
                self.run_command(f'rm -rf {file}', taskId='rm log', )
            if self.run_command(f'bash {sh} {" ".join([i[ii] for ii in args])}',taskId=f'{task_id}', ):  # 传递任意变量进入能解析到sh中
                continue
            else:  # 执行脚本内的错误捕捉输出
                # os.system(exit())
                return False
        if os.path.exists(file) == True:  # 捕捉自定义错误如checkip.sh中自定义的错误内容
            logger.info(f'{error_message}')
            return False
        else:
            self.run_command(f'touch  {file.split("/")[0]}/{file.split("/")[1]}/Success.log', taskId='success log', )
            #config.yaml配置文件重配置
            if f'{file.split("/")[0]}/{file.split("/")[1]}/Success.log' == 'initCheck/expectcheck/Success.log':  #
                for data in hostData['hosts']:
                    new_address=hostData['hosts'][hostData['hosts'].index(data)]['new_address'].split('/')[0]
                    hostData['hosts'][hostData['hosts'].index(data)]['last_address'] = new_address
                    if hostData['hosts'][hostData['hosts'].index(data)]['deploy'] == True:
                        self.deploy_ip = new_address

                # print(hostData['hosts'])
                with open('config.yaml', mode='w') as file:
                   file.write(yaml.dump(hostData, sort_keys=False))  # sort_keys保持原来的文件field顺序
                if self.run_command(f'sed -ri "s/deploy_ip:.*/deploy_ip: {self.deploy_ip}/g" config.yaml',taskId=f'change_deploy_ip' ) == False:
                   logger.info("config.yaml is failed Please  check it ")
            return True



    @classmethod
    def hostIni(self) -> str:
        config = configparser.ConfigParser(allow_no_value=True)  # 允许存放空值 默认是键值对存放
        config['master'], config['client'], config['server:children'], config['server:vars'],config['deploy_ip'] ,config['deploy_client']= {},{},{},{},{},{}
        masterList, clientList ,A_record=[], [], []
        config.set('server:children', 'master')
        config.set('server:children', 'client')
        with open('config.yaml', mode='r') as r:
            hostData = yaml.safe_load(r)
        #如果不配置第二次就无法读取到之前的self.deploy_ip因为可能上面Success.log的生成跳过了步骤
        for data in hostData['hosts']:  #要先生成deployip
            if hostData['hosts'][hostData['hosts'].index(data)]['deploy'] == True:
                deploy_ip = hostData['hosts'][hostData['hosts'].index(data)]['last_address']
        config.set('server:vars', 'deployIp', deploy_ip)
        config.set('deploy_ip', deploy_ip)
        for host in hostData['hosts']:
            config.set('server:vars', 'user', host['username'])
            A_record.append((host['hostname'],host['last_address'],host['password']))
            self.user=host['username']
            if host['master'] == True:
                config.set('master', host['last_address'])
                masterList.append((host['hostname'],host['last_address']))
                if deploy_ip!= host['last_address']:
                    config.set('deploy_client',host['last_address'] )
            else:
                config.set('client', host['last_address'])
                clientList.append((host['hostname'],host['last_address']))

        config.set('server:vars', 'master', str(masterList))
        config.set('server:vars', 'client', str(clientList))
        config.set('server:vars', 'dns_A_record', str(A_record) )
        config.set('server:vars', 'domain', 'uisee')

        with open('host.ini', mode='w') as r:
            config.write(r)
        return  self.user


if __name__ == '__main__':
    def loop(file, action, sh, error_message, task_id, *args):
        while True:
            if action(file, sh, error_message, task_id, *args) == True:
                # logger.info(r'Success！')
                break
            retry = input('是否重试？ y/n')
            if retry == 'y':
                continue
            else:
                os.system(exit())



    with open('stream.yaml', 'r') as f:
        stream = yaml.safe_load(f)

    deploy = Deployment()
    for i in stream['initasks']:
        dir = i["log"].split("/")[0] + '/' + i["log"].split("/")[1]
        if os.path.exists(f'{dir}/Success.log') == False:
            loop(i['log'], deploy.logic, i['sh'], i['error_message'], i['task_id'], *i['vars'])
        else:
            continue


    #根据文件生成ansible ini文件  master 放一堆  client放一堆，总的还要来一堆
    if os.path.exists(f'initCheck/ansiblecheck/Success.log') == True:
        user=Deployment.hostIni()
        from ansible_run_cmd import MyAnsiable2
        ansible = MyAnsiable2(remote_user=user)
        ansible.playbookRun()
    else:
        os.system(exit)






    #
    # 如果last_address和new_address不一致会导致断网，最好在console页面进行运行脚本

