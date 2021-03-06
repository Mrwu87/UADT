#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from prettytable import PrettyTable
import json
import shutil
import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.display import Display
import yaml
import os
import time
from mods.logs.log import service_logger

# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        # print(json.dumps({host.name: result._result}, indent=20))


    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result
        print(json.dumps({host.name: result._result}, indent=20))

#
# def main():
#     host_list = ['127.0.0.1']
#     # since the API is constructed for CLI it expects certain options to always be set in the context object
#     context.CLIARGS = ImmutableDict(connection='smart', module_path=['/to/mymodules', '/usr/share/ansible'], forks=10, become=None,
#                                     become_method=None, become_user=None, check=False, diff=False, verbosity=0)
#     # required for
#     # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
#     sources = ','.join(host_list)
#
#     if len(host_list) == 1:
#         sources += ','
#     # print(sources)
#     # initialize needed objects
#     loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
#     passwords = dict(vault_pass='secret')
#
#     # Instantiate our ResultsCollectorJSONCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
#     results_callback = ResultsCollectorJSONCallback()
#
#     # create inventory, use path to host config file as source or hosts in a comma separated string
#     inventory = InventoryManager(loader=loader, sources=sources)
#
#     # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
#     variable_manager = VariableManager(loader=loader, inventory=inventory)
#
#     # instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
#     # IMPORTANT: This also adds library dirs paths to the module loader
#     # IMPORTANT: and so it must be initialized before calling `Play.load()`.
#     tqm = TaskQueueManager(
#         inventory=inventory,
#         variable_manager=variable_manager,
#         loader=loader,
#         passwords=passwords,
#         stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
#     )
#
#     # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
#     play_source = dict(
#         name="Ansible Play",
#         hosts=host_list,
#         gather_facts='no',
#         tasks=[
#             # dict(action=dict(module='shell', args='ls'), register='shell_out'),
#             # dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}'))),
#             dict(action=dict(module='setup', args=dict(cmd=''))),
#         ]
#     )
#
#     # Create play object, playbook objects use .load instead of init or new methods,
#     # this will also automatically create the task objects from the info provided in play_source
#     play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
#
#     # Actually run it
#     try:
#         result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
#     finally:
#         # we always need to cleanup child procs and the structures we use to communicate with them
#         tqm.cleanup()
#         if loader:
#             loader.cleanup_all_tmp_files()
#
#     # Remove ansible tmpdir
#     shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
#
#     #?????????????????????
#     print("UP ***********")
#     for host, result in results_callback.host_ok.items():
#         print('{0} >>> {1}'.format(host, result._result['stdout']))
#
#     print("FAILED *******")
#     for host, result in results_callback.host_failed.items():
#         print('{0} >>> {1}'.format(host, result._result['stderr']))
#
#     print("DOWN *********")
#     for host, result in results_callback.host_unreachable.items():
#         print('{0} >>> {1}'.format(host, result._result['msg']))
#
#
# def playbook(playbooks):
#     host_list = ['127.0.0.1']
#     # since the API is constructed for CLI it expects certain options to always be set in the context object
#     context.CLIARGS = ImmutableDict(connection='smart', module_path=['/to/mymodules', '/usr/share/ansible-playbook'], forks=10,
#                                     become=None,
#                                     become_method=None, become_user=None, check=False, diff=False, verbosity=0)
#     # required for
#     # https://github.com/ansible/ansible/blob/devel/lib/ansible/inventory/manager.py#L204
#     sources = ','.join(host_list)
#
#     if len(host_list) == 1:
#         sources += ','
#     # print(sources)
#     # initialize needed objects
#     loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
#     passwords = dict(vault_pass='secret')
#
#     # Instantiate our ResultsCollectorJSONCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
#     results_callback = ResultsCollectorJSONCallback()
#
#     # create inventory, use path to host config file as source or hosts in a comma separated string
#     inventory = InventoryManager(loader=loader, sources=sources)
#
#     # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
#     variable_manager = VariableManager(loader=loader, inventory=inventory)
#
#     # instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
#     # IMPORTANT: This also adds library dirs paths to the module loader
#     # IMPORTANT: and so it must be initialized before calling `Play.load()`.
#
#     playbook = PlaybookExecutor(playbooks=playbooks,  # ???????????????????????????
#                                 inventory=inventory,
#                                 variable_manager=variable_manager,
#                                 loader=loader,
#                                 passwords=passwords)
#
#     # ??????????????????
#     playbook._tqm._stdout_callback = results_callback
#     result = playbook.run()
#     return result
#
# def get_result(result):
#     result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
#
#     # print(self.results_callback.host_ok)
#     for host, result in result.results_callback.host_ok.items():
#         result_raw['success'][host] = result._result
#     for host, result in result.results_callback.host_failed.items():
#         result_raw['failed'][host] = result._result
#     for host, result in result.results_callback.host_unreachable.items():
#         result_raw['unreachable'][host] = result._result
#
#     # ????????????????????????????????? JSON ???????????????
#     print(json.dumps(result_raw, indent=4))

    # result = playbook.run()
class MyAnsiable():
    Countine = True
    def __init__(self,
                 connection='smart',  # ???????????? local ???????????????smart ssh??????
                 remote_user=None,  # ????????????
                 ack_pass=None,  # ??????????????????
                 sudo=None,
                 sudo_user=None,
                 ask_sudo_pass=None,
                 module_path=None,  # ?????????????????????????????????????????????????????????
                 become=None,  # ????????????
                 become_method=None,  # ???????????? ?????? sudo ????????? su
                 become_user=None,  # ???????????????????????????????????????????????????
                 check=False, diff=False,
                 listhosts=None, listtasks=None, listtags=None,
                 verbosity=3,
                 syntax=None,
                 start_at_task=None,
                 inventory='mods/ansible/config/host.ini'):  #??????inventory???????????? ???master.ini node.ini ??????yaml??????????????????all????????????

        # ??????????????????
        """
        ????????????????????????????????????????????????
        ??????????????????????????????????????????????????????????????????
        """
        context.CLIARGS = ImmutableDict(
            connection=connection,
            remote_user=remote_user,
            ack_pass=ack_pass,
            sudo=sudo,
            sudo_user=sudo_user,
            ask_sudo_pass=ask_sudo_pass,
            module_path=module_path,
            become=become,
            become_method=become_method,
            become_user=become_user,
            verbosity=verbosity,
            listhosts=listhosts,
            listtasks=listtasks,
            listtags=listtags,
            syntax=syntax,
            start_at_task=start_at_task,
        )

        # ???????????????????????????????????? inventory, ????????? "localhost,"
        # ?????? inventory ??????
        self.inventory = inventory if inventory else "localhost"  #??????????????????localhost

        # ????????????????????????
        self.loader = DataLoader()

        # ????????? ??????????????????
        self.inv_obj = InventoryManager(loader=self.loader, sources=self.inventory)

        # ?????????????????????????????????????????????????????????
        self.passwords = {}

        # ???????????????????????????
        self.results_callback = ResultsCollectorJSONCallback()

        # ???????????????
        self.variable_manager = VariableManager(self.loader, self.inv_obj)

    def run(self, hosts='localhost', gether_facts="no", module="ping", args='') -> None:
        play_source = dict(
            name="Ad-hoc",
            hosts=hosts,
            gather_facts=gether_facts,
            tasks=[
                # ???????????? task ???????????????????????????????????????????????????????????????
                # ????????????????????????????????????????????????????????????
                {"action": {"module": 'setup', "args": args}},
            ])

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inv_obj,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.results_callback)

            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def playbook(self, playbooks) -> None:
        from ansible.executor.playbook_executor import PlaybookExecutor

        playbook = PlaybookExecutor(playbooks=playbooks,  # ???????????????????????????
                                    inventory=self.inv_obj,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader,
                                    passwords=self.passwords)

        # ??????????????????
        playbook._tqm._stdout_callback = self.results_callback

        result = playbook.run()

    def get_fact_result(self) -> str:  #????????????????????????
        result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}

        # print(self.results_callback.host_ok)
        for host, result in self.results_callback.host_ok.items():
            result_raw['success'][host] = result._result
        for host, result in self.results_callback.host_failed.items():
            result_raw['failed'][host] = result._result
            service_logger.info(result_raw['failed'][host])
        for host, result in self.results_callback.host_unreachable.items():
            result_raw['unreachable'][host] = result._result
            service_logger.info(result_raw['unreachable'][host])

        # ????????????????????????????????? JSON ???????????????
        result=result_raw['success']
        result_list=[]
        for i in result:
            re=eval(result[i]['msg'])
            # print(type(re))
            result_list.append(json.loads(re))

        currentEnvTable = PrettyTable(['Hostname','Address', 'OS','vcpu', 'Kernel', 'Disk', 'x64/x32','Mem_total','Mem_free','python_version','datetime'])

        for ii in result_list:
            if int(ii['Disk'][:-1]) <= 10 or round(float(ii['Mem_free'][:-1]),2) <= 2.0 or int(ii['vcpu']) < 2 :   #????????????????????????????????????????????????????????????disk?????????G mem?????????M
                service_logger.info(f"{ii['Address']} this system is not avaible")
                self.Countine = False
            total=str(round(float(ii['Mem_total'][:-1]),2))+'G'
            free=str(round(float(ii['Mem_free'][:-1]),2))+'G'
            currentEnvTable.add_row([ii['Hostname'],ii['Address'], ii['OS'], ii['vcpu'],ii['Kernel'], ii['Disk'], ii['x64/x32'],total,free,ii['python_version'],ii['datetime']])
        print(currentEnvTable)

    def get_result(self,dir) -> bool:  #????????????????????????
        result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        # print(self.results_callback.host_ok)
        for host, result in self.results_callback.host_ok.items():
            result_raw['success'][host] = result._result
        for host, result in self.results_callback.host_failed.items():
            result_raw['failed'][host] = result._result
        for host, result in self.results_callback.host_unreachable.items():
            result_raw['unreachable'][host] = result._result
        # ????????????????????????????????? JSON ???????????????
        # if result_raw['success'] == {}:
        #     with open('Stepfiles/Success.log','w') as f:
        #         f.write(result_raw)
        if result_raw['failed'] == {} and result_raw['unreachable'] == {}:
            with open(f'{dir}/Success.log', 'w') as f:
                f.write('Success')

        if result_raw['failed'] != {} or result_raw['unreachable']  != {}:
            service_logger.info(result_raw)
            return False
            # with open(f'{dir}/xxx.log','w') as f:
            #     f.write(result_raw)

    def playbookRun(self) -> None:
        # ansible2 = MyAnsiable2(remote_user=user)
        with open('config/yaml/stream.yaml', 'r') as f:
            self.stream = yaml.safe_load(f)
        import enlighten
        display = Display()
        display.verbosity = 6
        manager = enlighten.get_manager()
        pbar = manager.counter(total=len(self.stream['ansibletasks'])-1, desc='Run ansibletasks')
        for i in self.stream['ansibletasks']:
            dir = "/".join([ s for s in  i['log'].split("/")[0:-1]])
            if i["playbookfile"].split("/")[-1] == 'getSysinfo.yaml':
                self.playbook([i["playbookfile"], ])
                self.get_fact_result()
                continue
            self.Countine=True
            if self.Countine:
                time.sleep(0.3)
                pbar.update()
                if os.path.exists(f'{dir}/Success.log') == False:
                    self.playbook([i["playbookfile"], ])
                    if self.get_result(dir)==False:
                        service_logger.info(f'{i["playbookfile"]} This file  execute failed')
                        break  #???????????????????????????????????? ??????????????????failed

                else:  #????????????success.log???????????????
                    continue

            else:
                service_logger.info('This system is not ready')
                break
        manager.stop()



