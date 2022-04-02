import subprocess
import json, yaml
from log import logger
from datetime import datetime, timedelta
from time import sleep


class deplopy:
    # @classmethod
    # def subprocess_popen(self, statement, workdir):
    #     print(workdir)
    #     p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE, cwd=workdir)  # 执行shell语句并定义输出格式
    #     while p.poll() == None:  # 判断进程是否结束（Popen.poll()用于检查子进程（命令）是否已经执行结束，没结束返回None，结束后返回状态码）
    #         if p.wait() != 0:  # 判断是否执行成功（Popen.wait()等待子进程结束，并返回状态码；如果设置并且在timeout指定的秒数之后进程还没有结束，将会抛出一个TimeoutExpired异常。）
    #             log  hosts: 127.0.0.1ger.info(f'\n{statement} 命令执行失败!！')
    #             return False
    #         else:
    #             re = p.stdout.readlines()  # 获取原始执行结果
    #             logger.info(f'\n{statement}命令执行成功！！')
    #             for i in range(len(re)):  # 由于原始结果需要转换编码，所以循环转为utf8编码并且去除\n换行
    #                 res = re[i].decode('utf-8')
    #                 logger.info(f'\n{res}')

    @classmethod
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
                if popen.poll() is not None:
                    break
                stdout, stderr = popen.communicate()
                stdout_text = (stdout.decode('utf8')).strip()
                stderr_text = stderr.decode('utf8')
                print(stdout_text)
                print(stderr_text)
                sleep(0.1)
                if end_time <= datetime.now():
                    popen.kill()
                    logger.critical('[COMMAND] [%s] EXEC TIMEOUT' % (taskId))
                    return False, None, None

            if popen.returncode > 0:
                logger.info('[COMMAND] [%s] FAILED:[%s], CODE:[%s], \nSTDOUT:[\n%s\n]\nSTDERR:[\n%s\n]' % (
                    taskId, command, popen.returncode, stdout_text, stderr_text))
                return False, stdout_text, stderr_text
            else:
                logger.info('[COMMAND] [%s] SUCCESS:[%s], CODE:[%s]' %
                            (taskId, command, popen.returncode))
                return True, stdout_text, stderr_text
        except Exception as e:
            logger.exception('[COMMAND] [%s] EXCEPTION:[%s]:' % (taskId, command))
            return False, None, None


if __name__ == '__main__':

    with open('autoconfig.yaml', mode='r') as r:
        a = yaml.safe_load(r)
    sh = f'''echo {a["data"]["deploy_password"]} | sudo -S chmod +w /etc/sudoers
    sudo sed -i '26,26s/ALL=(ALL:ALL) ALL/ALL=(ALL:ALL) NOPASSWD:ALL/g' /etc/sudoers
    tar -xvf pip-22.0.3.tar.gz
    cd pip-22.0.3/
    pwd
    sudo python3 setup.py install
    cd .
    pwd
    sudo tar -zxvf   cmd2-2.4.0.tar.gz
    sudo tar -zxvf   ansible5.4.tar.gz
    sudo tar -zxvf   argparse-1.4.0.tar.gz
    sudo pip install --no-index --find-links=.  ansible
    sudo pip install --no-index --find-links=.  cmd2
    sudo pip install --no-index --find-links=.  argparse'''
    sh = sh.split('\n')
    workdir = '.'
    for i in sh:
        if i[0:3] == 'cd ':
            workdir = i[3:]
            continue

        deplopy.run_command(i, taskId='install_Ansible', cwd=workdir)




#     with open('autoconfig.yaml', mode='r') as r:
#         a = yaml.safe_load(r)
#     sh = f''''''
#     sh = sh.split('\n')
#     print(sh)
#     workdir = '.'
#
#     if workdir[0:3] == 'cd ':
#         workdir = workdir[3:]
#

