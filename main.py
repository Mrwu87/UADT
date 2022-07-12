# import os
# from mods.services.deployment import Deployment
# from mods.ansible.host_ini import hostIni
# if __name__ == '__main__':
#     deploy=Deployment()
#     App,count=deploy.Start()
#     if os.path.exists(f'mods/services/config/ansiblecheck/Success.log') == True:
#         user=hostIni()
#         from mods.ansible.ansible import MyAnsiable
#         ansible = MyAnsiable(remote_user=user)
#         ansible.playbookRun(App,count)
#     else:
#         os.system(exit)
import yaml
import time
import threading
import tailf
from mods.services.deployment import Deployment
from mods.ansible.host_ini import hostIni
import os, sys
import npyscreen

class Npy(npyscreen.NPSApp):
    def thread_log(self):
        self.ml = self.F.add(npyscreen.BoxTitle, name='Running Logs....', scroll_exit=True, slow_scroll=True,
                             rely=self.F.nextrely + 1)
        log_file = '/home/wlw/UADT/mods/logs/config/runtime'
        txt = ''
        time.sleep(2)   #防止程序开头显示乱码，缓一下
        with tailf.Tail(log_file) as tail:
            while True:

                for event in tail:
                    if isinstance(event, bytes):
                        # txt = txt[-3000:-1]+event.decode('utf-8')
                        txt = txt + event.decode('utf-8')
                text = txt.split('\n')
                text.reverse()
                for i in text:
                    if i[190:] != '': #每行只取出190个字符 超过的就接入下一行
                        text.insert(text.index(i) + 1, i[190:])
                        text[text.index(i)] = i[:190]
                self.ml.values = text[:200]
                time.sleep(1.5)  # 刷新率不能低过1.5秒
                self.ml.display()  #局部控件更新




    def main(self):
        with open('config/yaml/stream.yaml', 'r') as f:
            stream = yaml.safe_load(f)
        self.total_task = len(stream['initasks']) + len(stream['ansibletasks'])
        self.F = npyscreen.Form(name='Welcome to UADT', lines=0, columns=0, labelColor='CONTROL')
        self.run_status = self.F.add(npyscreen.TitleText, name="Status:", editable=False, value='Running', relx=-40,
                                     color='DANGER')
        self.file_status = self.F.add(npyscreen.TitleText, name="ExecFile:", editable=False, value='', relx=-40)
        t = self.F.add(npyscreen.MultiLineEdit, value=
        '''         $$\   $$\  $$$$$$\  $$$$$$$\ $$$$$$$$|
         $$ |  $$ |$$  __$$\ $$  __$$\\ __$$ __|
         $$ |  $$ |$$ /  $$ |$$ |  $$ |  $$ |
         $$ |  $$ |$$$$$$$$ |$$ |  $$ |  $$ |
         $$ |  $$ |$$  __$$ |$$ |  $$ |  $$ |
         $$ |  $$ |$$ |  $$ |$$ |  $$ |  $$ |
         \$$$$$$  |$$ |  $$ |$$$$$$$  |  $$ |
           \______/ \__|  \__|\_______/   \__|''', max_height=10, editable=False, color='CONTROL')  # color 字体颜色

        self.vc = self.F.add(npyscreen.TitleSliderPercent, out_of=int(self.total_task), value=0, name='ProgressBar',
                             editable=False)

        self.F.add(npyscreen.TitleText, name='LogFile:', editable=False, value='~/UADT/mods/logs/config/runtime',
                   rely=self.F.nextrely + 1)
        # pid=os.getpid()
        # print(pid)
        # self.F.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.exit_application
        t1 = threading.Thread(target=self.thread_log, args=())
        t1.setDaemon(True)
        t1.start()
        # self.F.display()

        deploy = Deployment()
        count = deploy.Start(self)
        if os.path.exists(f'mods/services/config/ansiblecheck/Success.log') == True:
            user = hostIni()
            from mods.ansible.ansible import MyAnsiable
            ansible = MyAnsiable(remote_user=user)
            ansible.playbookRun(self, count)
        else:
            os.system(exit)
        self.F.edit()  #最后阻塞



if __name__ == "__main__":
    App = Npy()
    App.run()