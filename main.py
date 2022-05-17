import os
from mods.services.deployment import Deployment
from mods.ansible.host_ini import hostIni
# from mods.commands.command import Command
if __name__ == '__main__':
    # common = Command()
    # try:
    #     import npyscreen, tailf
    # except Exception as e:
    #     common.run_command(f'bash  mods/services/config/sh/npyscreen_instll.sh ', taskId=f'install npyscreen')
    deploy=Deployment()
    App,count=deploy.Start()
    if os.path.exists(f'mods/services/config/ansiblecheck/Success.log') == True:
        user=hostIni()
        from mods.ansible.ansible import MyAnsiable
        ansible = MyAnsiable(remote_user=user)
        ansible.playbookRun(App,count)
    else:
        os.system(exit)