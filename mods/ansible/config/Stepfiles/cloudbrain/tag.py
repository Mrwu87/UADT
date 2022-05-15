import sys
import subprocess
import json, yaml
from log import logger
from datetime import datetime, timedelta
from time import sleep
import re
class deplopy:
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

with open(f'{sys.argv[2]}images_tongyong.txt') as f:
    a=f.readlines()

for i in a:
    counts=i.count('/')
    if counts >= 2:
        new=i.replace(i.split('/')[0],sys.argv[1])
    if counts == 1:
        new=sys.argv[1]+'/'+i
    if counts == 0:
        new = sys.argv[1] + '/' + 'library/' + i
    command=f'sudo docker tag {i.strip()} {new}'
    deplopy.run_command(command, taskId='push images_tag')
    # if i.strip() == 'busybox:1.30.1':
    #     command = f'sudo docker tag busybox:lastest {sys.argv[1]}/library/busybox:lastest'
    #     deplopy.run_command(command, taskId='push images_tag')
    #     command = f'sudo docker push {sys.argv[1]}/library/busybox:lastest'
    #     deplopy.run_command(command, taskId='push images_tag')
    command=f'sudo docker push {new}'
    deplopy.run_command(command, taskId='push images_tag')


with open(f'{sys.argv[2]}repo_charts.yaml', mode='r') as r:
    a = yaml.safe_load(r)
for i in a:
    chart_registry=a[i]['CHART_VER'].split('/')[0]
    version = re.findall('[v]?\d+\.\d+.\d+', a[i]['CHART_VER'])
    chart_version = a[i]['CHART_VER'].split(' ')[0]
    add_repo_command = f'helm repo add {chart_registry}  http://{sys.argv[1]}/chartrepo/{chart_registry}/'
    deplopy.run_command(add_repo_command, taskId='add helm repo ')
    file=f"{a[i]['CHART_VER'].split('/')[1].split(' ')[0]}-{version[0]}.tgz  {chart_registry}"
    with open(f'{sys.argv[2]}charts.txt','a') as f:
        f.write(file+'\n')

with open(f'{sys.argv[2]}charts.txt') as f:
    a = f.readlines()
for chart in a:
    command=f'helm cm-push  {sys.argv[3]}{chart.split(" ")[0].strip()}  {chart.split(" ")[2].strip()}  -u admin -p uisee123.'
    # print(command)
    deplopy.run_command(command, taskId='push chart ')






