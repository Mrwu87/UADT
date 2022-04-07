import os
from mods.services.deployment import Deployment
from mods.ansible.host_ini import hostIni
if __name__ == '__main__':
    deploy=Deployment()
    deploy.Start()

    if os.path.exists(f'mods/services/config/ansiblecheck/Success.log') == True:
        user=hostIni()
        from mods.ansible.ansible import MyAnsiable
        ansible = MyAnsiable(remote_user=user)
        ansible.playbookRun()
    else:
        os.system(exit)