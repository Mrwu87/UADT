# from retrying import retry
# import time
# from threading import Thread
# abc=True
# def counter():
#     time_left = 2
#     while time_left > 0:
#         print('倒计时(s):', time_left)
#         time.sleep(1)
#         time_left = time_left - 1
#     if time_left == 0:
#
#
# # def panduan():
# #     global abc
# #     while 1:
# #         abc=True
# #     else:
#
#
#
#
# def task():
#     th1 = Thread(target=counter, args=())
#     # th2 = Thread(target=panduan, args=())
#     th1.start()
#     for  a in range(3):
#         print(123456767777)
#         print(123456767777)
#         print(123456767777)
#         time.sleep(10)
#         print('end')
#
#
#
# task()
from func_timeout import func_set_timeout
import func_timeout
import time
@func_set_timeout(3)#设定函数超执行时间_
def task():
    print('hello world')
    time.sleep(5)
    return '执行成功_未超时'
if __name__ == '__main__':
    for i in range(3):
        try:
            print(task())
            break
        #若调用函数超时自动走异常(可在异常中写超时逻辑处理)
        except func_timeout.exceptions.FunctionTimedOut:
            continue

            # if self.Countine:
            #     #time.sleep(0.3)
            #     #pbar.update()
            #     if os.path.exists(f'{dir}/Success.log') == False:
            #         for s in range(3):
            #          try:
            #           App.F.DISPLAY()
            #           self.playbook([i["playbookfile"], ])
            #           self.get_result(dir)
            #           break
            #          except func_timeout.exceptions.FunctionTimedOut:
            #           service_logger.info('timeout')
            #           service_logger.info('timeout')
            #           service_logger.info('timeout')
            #           time.sleep(5)
            #           continue
            #         # if self.get_result(dir)==False:
            #         if self.result != 0:
            #             service_logger.info(f'{i["playbookfile"]} This file  execute failed')
            #             App.run_status.set_value('Error')
            #             break  #有失败消息的直接退出循环 并且打印文件failed
            #         App.vc.set_value(ansible_count)
            #         App.vc.display()
            #         success_count+=1
            #     else:  #对于生成success.log的直接放过
            #         App.vc.set_value(ansible_count)
            #         App.vc.display()
            #         success_count += 1
            #         continue
            #
            #
            # if self.Countine:
            #     # time.sleep(0.3)
            #     # pbar.update()
            #     if os.path.exists(f'{dir}/Success.log') == False:
            #         for s in range(3):
            #             try:
            #                 App.F.DISPLAY()
            #                 self.playbook([i["playbookfile"], ])
            #                 self.get_result(dir)
            #                 break
            #             except func_timeout.exceptions.FunctionTimedOut:
            #                 service_logger.info('Playbook Execution timed out ! We will restart the playbook')
            #                 time.sleep(5)
            #                 continue
