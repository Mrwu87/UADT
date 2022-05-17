import asyncio
import npyscreen
import time
import threading
import tailf


class Npy(npyscreen.NPSApp):
    def thread_log(self):
        self.ml = self.F.add(npyscreen.BoxTitle ,name='Running Log....', scroll_exit=True, slow_scroll=True,rely=self.F.nextrely+1,color='DANGER')
        log_file='/home/wlw/UADT/mods/logs/config/runtime'
        txt=''
        with tailf.Tail(log_file) as tail:
           while True:

                for event in tail:
                    if isinstance(event, bytes):
                        txt = txt[-3000:-1]+event.decode('utf-8')
                text = txt.split('\n')
                text.reverse()
                for i in text:
                    if i[190:] != '':
                        text.insert(text.index(i)+1, i[190:])
                        text[text.index(i)]=i[:190]

                self.ml.values=text
                self.ml.display()
                #time.sleep(1.2)   #刷新率不能低过




    async def npy_run(self):
        self.F = npyscreen.Form(name='Welcome to UADT', lines=0, columns=0, labelColor='CONTROL')
        t = self.F.add(npyscreen.MultiLineEdit, value=
        '''         $$\   $$\  $$$$$$\  $$$$$$$\ $$$$$$$$|
         $$ |  $$ |$$  __$$\ $$  __$$\\ __$$ __|
         $$ |  $$ |$$ /  $$ |$$ |  $$ |  $$ |
         $$ |  $$ |$$$$$$$$ |$$ |  $$ |  $$ |
         $$ |  $$ |$$  __$$ |$$ |  $$ |  $$ |
         $$ |  $$ |$$ |  $$ |$$ |  $$ |  $$ |
         \$$$$$$  |$$ |  $$ |$$$$$$$  |  $$ |
           \______/ \__|  \__|\_______/   \__|''', max_height=10, editable=False, color='CONTROL')  # color 字体颜色

        self.vc = self.F.add(npyscreen.TitleSliderPercent, out_of=17, value=0, name='进度条', editable=False)

        self.F.add(npyscreen.TitleText, name='日志位置', editable=False, value='/var/log/nginx/wwa',
                   rely=self.F.nextrely + 1)

        # self.F.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.exit_application
        t1 = threading.Thread(target=self.thread_log, args=())
        #t1.setDaemon(True)
        t1.start()



    def main(self):
        asyncio.run(self.npy_run())