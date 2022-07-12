'''
Date: 2021-06-24 21:33:33
LastEditors: yuxuan.liu@uisee.com
LastEditTime: 2022-01-09 17:34:47
FilePath: /data/config-sync/console_standalone.py
Description: 
'''

import json
from mods.logs.log import service_logger
import requests
import sys
import urllib3
from ruamel import yaml
urllib3.disable_warnings()

class ConsoleImporter:
    def __init__(self) -> None:
        self.clusterConsole = sys.argv[1]
        self.smoketestProject = sys.argv[2]
        if not self.clusterConsole.endswith('/'):
            self.clusterConsole = self.clusterConsole + '/'
        self.baseconfPath = f'{sys.argv[3]}/'

        loginUrl = self.clusterConsole + 'api/console/system/security/login'

        self.s = requests.Session()

        self.adminAccount = {'username': 'admin',
                             'password': 'uisee@future'}
        service_logger.info('[CONSOLE] Logging in, by admin user....')
        self.s.post(url=loginUrl, data=self.adminAccount, verify=False)


    def addResource(self):
        reousrceUrl = 'api/console/system/resources'

        resourcePath = '%sconsole_configs/resources.json' % self.baseconfPath

        jsonData = json.load(
            open(resourcePath, mode='rt', encoding='utf-8'))
        for j in jsonData:
            service_logger.info('[CONSOLE]  Imported [Console] [Resource] [%s]' %
                        (j['code']))
            self.s.post(url=self.clusterConsole +
                        reousrceUrl, json=j, verify=False)

    def addService(self):
        kongUri = 'api/console/system/internal/kongServices'
        serviceUrl = 'api/console/system/services'
        reousrceUrl = 'api/console/system/resources'

        kongServicesList = self.s.get(
            url=self.clusterConsole+kongUri, verify=False).json()['kongServices']
        resourceList = self.s.get(
            url=self.clusterConsole+reousrceUrl, verify=False).json()['resources']
        serviceList = self.s.get(
            url=self.clusterConsole+serviceUrl, verify=False).json()['services']

        servicrePath = '%sconsole_configs/services.json' % self.baseconfPath
        jsonData = json.load(
            open(servicrePath, mode='rt', encoding='utf-8'))

        existedServiceList = []
        for svc in serviceList:
            existedServiceList.append(svc['name'])
        # Below loop added service with resource, without apis.
        for i in jsonData:
            if i['name'] in existedServiceList:
                service_logger.info('[CONSOLE] Service: %s existed, ignored.' % i['name'])
                continue
            for k in kongServicesList:
                if i['externalName'] == k['name'].split('.')[0]:
                    resourceUUIDs = []
                    for r in i['resources']:
                        for res in resourceList:
                            if r['code'] == res['code']:
                                resourceUUIDs.append(res['uuid'])
                    j = {"name": i['name'],
                         "externalId": k['id'],
                         "resourceUUIDs": resourceUUIDs
                         }
                    service_logger.info('[CONSOLE] Imported [Console] [Service] [%s - %s]' %
                                (j['name'], j['externalId']))
                    self.s.post(url=self.clusterConsole +
                                serviceUrl, verify=False, json=j)
                    service_logger.info('[CONSOLE] Service json dump: %s' % j)
                    break

        # Add service with apis.
        serviceList = self.s.get(
            url=self.clusterConsole+serviceUrl, verify=False).json()['services']
        for svc in serviceList:
            apiUrl = 'api/console/system/services/%s/apis' % svc['uuid']
            service_logger.info('[CONSOLE] > Start import service: %s API.' % (svc['name']))
            for i in jsonData:
                if i['name'] == svc['name']:
                    for api in i['apis']:
                        j = {'title': api['title'],
                             'path': api['path'],
                             'method': api['method']}
                        r = self.s.post(url=self.clusterConsole +
                                        apiUrl, verify=False, json=j)
                        if r.status_code == 201:
                            service_logger.info('[CONSOLE] - Add API success: [%6s] [%s] [%s]' % (
                                api['method'], api['title'], api['path']))
                        elif r.status_code == 400:
                            try:
                                if r.json()['description'] == "api with same method/path already exists":
                                    service_logger.warning('[CONSOLE] - Add API ignored: [%6s] [%s] [%s] : %s' % (
                                        api['method'], api['title'], api['path'], 'api with same method/path already exists'))
                            except:
                                service_logger.warning('[CONSOLE] - Add API failed: [%6s] [%s] [%s] res: %s' % (
                                    api['method'], api['title'], api['path'], r.json()))
                        else:
                            service_logger.error(('- Add API failed: [%6s] [%s] [%s], error: %s' % (
                                api['method'], api['title'], api['path'], r.text)))
            service_logger.info('[CONSOLE] > Stop import service: %s API.' % (svc['name']))

    def addScope(self):
        scopeUri = 'api/console/system/scopes'
        serviceUrl = 'api/console/system/services'

        scopePath = '%sconsole_configs/scopes.json' % self.baseconfPath

        jsonData = json.load(
            open(scopePath, mode='rt', encoding='utf-8'))

        scopeList = self.s.get(
            url=self.clusterConsole+scopeUri, verify=False).json()['scopes']

        serviceList = self.s.get(
            url=self.clusterConsole+serviceUrl, verify=False).json()['services']

        existedScopeDict = {}
        if scopeList == []:
            service_logger.warning('[CONSOLE] > There was no scope on console.')
        else:
            for s in scopeList:
                existedScopeDict[s['name']] = s['uuid']
                if s['children'] == None:
                    pass
                else:
                    for child in s['children']:
                        existedScopeDict[child['name']] = child['uuid']

        for j in jsonData:
            if j['name'] in existedScopeDict:
                # The scope existed on console.
                parentUUID = existedScopeDict[j['name']]
                service_logger.warning(
                    '> Scope existed on console, %s. Ignored.' % (j['name']))
                if j['children'] == None:
                    if j['apis'] == None:
                        service_logger.info('[CONSOLE] - There was no API under scope: %s.' %
                                    (j['name']))
                    else:
                        service_logger.info('[CONSOLE] - Refresh API to scope: %s.' %
                                    (j['name']))
                        apiUUIDs = []
                        for api in j['apis']:
                            for svc in serviceList:
                                for a in svc['apis']:
                                    method = api.split(',')[0]
                                    path = api.split(',')[1]
                                    if method == a['method'] and path == a['path']:
                                        apiUUIDs.append(a['uuid'])
                        apiUUIDsDic = {"apiUUIDs": apiUUIDs}
                        self.s.put(url='%sapi/console/system/scopes/%s/apis' %
                                   (self.clusterConsole, parentUUID), verify=False, json=apiUUIDsDic)
                        service_logger.info(
                            '[CONSOLE] - Refresh API to scope: %s, dump api UUID: %s' % (j['name'], apiUUIDs))
                else:
                    for child in j['children']:
                        childUUIDList = []
                        if child['name'] in existedScopeDict:
                            childUUID = existedScopeDict[child['name']]
                            if child['apis'] == None:
                                # No API under this scope.
                                service_logger.info('[CONSOLE] - There was no API under child scope: %s.' %
                                            (child['name']))
                            else:
                                # Existed API under this scope.
                                service_logger.info(
                                    '[CONSOLE] - Try to refresh API to child scope: %s.' % (child['name']))
                                apiUUIDs = []
                                for api in child['apis']:
                                    for svc in serviceList:
                                        for a in svc['apis']:
                                            method = api.split(',')[0]
                                            path = api.split(',')[1]
                                            if method == a['method'] and path == a['path']:
                                                apiUUIDs.append(a['uuid'])
                                apiUUIDsDic = {"apiUUIDs": apiUUIDs}
                                r = self.s.put(url='%sapi/console/system/scopes/%s/apis' % (
                                    self.clusterConsole, childUUID), verify=False, json=apiUUIDsDic)
                                service_logger.info(
                                    '[CONSOLE] - Refresh API to child scope: %s, dump api UUID: %s, response: %s' % (child['name'], apiUUIDs, r.json()))
                        else:
                            l2data = {
                                "name": child['name'],
                                "code": child['code'],
                                "domain": child['domain'],
                                "isRoot": child['isRoot'],
                                "isParent": child['isParent'],
                                "roles": child['roles']
                            }
                            cr = self.s.post(url=self.clusterConsole +
                                             scopeUri, verify=False, json=l2data)
                            childUUID = cr.json()['scope']['uuid']
                            childUUIDList.append(childUUID)
                            service_logger.info(
                                '[CONSOLE] - Add child Scope success, scop: %s,dump: %s' % (l2data['name'], cr.json()))

                            if child['apis'] == None:
                                # No apis under child.
                                service_logger.info('[CONSOLE] - There was no API under child scope: %s.' %
                                            (child['name']))
                            else:
                                # Apis under child.
                                service_logger.info(
                                    '[CONSOLE] - Add API to child scope: %s.' % (child['name']))
                                apiUUIDs = []
                                for api in child['apis']:
                                    for svc in serviceList:
                                        for a in svc['apis']:
                                            method = api.split(',')[0]
                                            path = api.split(',')[1]
                                            if method == a['method'] and path == a['path']:
                                                apiUUIDs.append(a['uuid'])
                                apiUUIDsDic = {"apiUUIDs": apiUUIDs}
                                self.s.put(url='%sapi/console/system/scopes/%s/apis' % (
                                    self.clusterConsole, childUUID), verify=False, json=apiUUIDsDic)
                                service_logger.info(
                                    '[CONSOLE] - Add API to child scope: %s, dump api UUID: %s' % (child['name'], apiUUIDs))
            else:
                # The scope NOT existed on console.
                l1data = {
                    "name": j['name'],
                    "code": j['code'],
                    "domain": j['domain'],
                    "isRoot": j['isRoot'],
                    "isParent": j['isParent'],
                    "roles": j['roles']
                }
                pr = self.s.post(url=self.clusterConsole +
                                 scopeUri, verify=False, json=l1data)
                parentUUID = pr.json()['scope']['uuid']
                service_logger.info('[CONSOLE] > Add Scope success, scop: %s. dump: %s, resp:%s' %
                            (l1data['name'], l1data, pr.json()))

                if j['children'] == None:
                    # No Child under this scope.
                    service_logger.info('[CONSOLE] - There was no child under scope: %s.' %
                                (j['name']))

                    if j['apis'] == None:
                        # No API under this scope.
                        service_logger.info('[CONSOLE] - There was no API under scope: %s.' %
                                    (j['name']))
                    else:
                        # Existed API under this scope.
                        service_logger.info('[CONSOLE] - Add API to scope: %s.' % (j['name']))
                        apiUUIDs = []
                        for api in j['apis']:
                            for svc in serviceList:
                                for a in svc['apis']:
                                    method = api.split(',')[0]
                                    path = api.split(',')[1]
                                    if method == a['method'] and path == a['path']:
                                        apiUUIDs.append(a['uuid'])
                        apiUUIDsDic = {"apiUUIDs": apiUUIDs}
                        self.s.put(url='%sapi/console/system/scopes/%s/apis' %
                                   (self.clusterConsole, parentUUID), verify=False, json=apiUUIDsDic)
                        service_logger.info(
                            '[CONSOLE] - Add API to scope: %s, dump api UUID: %s' % (j['name'], apiUUIDs))

                else:
                    # Existed child under scope.
                    childUUIDList = []
                    for child in j['children']:
                        if child['name'] in existedScopeDict:
                            # The chiled existed on console.
                            childUUIDList.append(
                                existedScopeDict[child['name']])
                            service_logger.warning(
                                '- Scope existed on console, %s. Ignored.' % (child['name']))
                            if child['apis'] == None:
                                # No API under this scope.
                                service_logger.info('[CONSOLE] - There was no API under child scope: %s.' %
                                            (child['name']))
                            else:
                                # Existed API under this scope.
                                service_logger.info(
                                    '- Try to refresh API to child scope: %s.' % (child['name']))
                                apiUUIDs = []
                                for api in child['apis']:
                                    for svc in serviceList:
                                        for a in svc['apis']:
                                            method = api.split(',')[0]
                                            path = api.split(',')[1]
                                            if method == a['method'] and path == a['path']:
                                                apiUUIDs.append(a['uuid'])
                                apiUUIDsDic = {"apiUUIDs": apiUUIDs}

                                self.s.put(url='%sapi/console/system/scopes/%s/apis' % (
                                    self.clusterConsole, childUUID), verify=False, json=apiUUIDsDic)
                                service_logger.info(
                                    '- Refresh API to child scope: %s, dump api UUID: %s' % (child['name'], apiUUIDs))

                        else:
                            # The chiled not existed on console.
                            l2data = {
                                "name": child['name'],
                                "code": child['code'],
                                "domain": child['domain'],
                                "isRoot": child['isRoot'],
                                "isParent": child['isParent'],
                                "roles": child['roles']
                            }
                            cr = self.s.post(url=self.clusterConsole +
                                             scopeUri, verify=False, json=l2data)
                            childUUID = cr.json()['scope']['uuid']
                            childUUIDList.append(childUUID)
                            service_logger.info(
                                '[CONSOLE] - Add child Scope success, scop: %s,dump: %s.' % (l2data['name'], cr.json()))

                            if child['apis'] == None:
                                # No apis under child.
                                service_logger.info('[CONSOLE] - There was no API under child scope: %s.' %
                                            (child['name']))
                            else:
                                # Apis under child.
                                service_logger.info(
                                    '[CONSOLE] - Add API to child scope: %s.' % (child['name']))
                                apiUUIDs = []
                                for api in child['apis']:
                                    for svc in serviceList:
                                        for a in svc['apis']:
                                            method = api.split(',')[0]
                                            path = api.split(',')[1]
                                            if method == a['method'] and path == a['path']:
                                                apiUUIDs.append(a['uuid'])
                                apiUUIDsDic = {"apiUUIDs": apiUUIDs}
                                self.s.put(url='%sapi/console/system/scopes/%s/apis' % (
                                    self.clusterConsole, childUUID), verify=False, json=apiUUIDsDic)
                                service_logger.info(
                                    '[CONSOLE] - Add API to child scope: %s, dump api UUID: %s' % (child['name'], apiUUIDs))

                    # Attach children to parent.
                    parentUri = 'api/console/system/scopes/%s/children' % (
                        parentUUID)
                    children = {"scopeUUIDs": childUUIDList}
                    service_logger.info('[CONSOLE] > Attach children to parent scope: %s, DUMP childUUIDList: %s' % (
                        parentUUID, childUUIDList))
                    self.s.put(url=self.clusterConsole + parentUri,
                               verify=False, json=children)

    def associateScope(self):
        reousrceUrl = 'api/console/system/resources'
        componentUri = 'api/console/components'
        scopeUri = 'api/console/system/scopes'
        componentsPath = '%sconsole_configs/components.json' % self.baseconfPath
        jsonData = json.load(
            open(componentsPath, mode='rt', encoding='utf-8'))
        service_logger.info('[CONSOLE] > [Start] Create component.')
        for j in jsonData:
            data = {
                "name": j['name'],
                "code": j['code']
            }
            r = self.s.post(url=self.clusterConsole +
                            componentUri, verify=False, json=data)
            if r.status_code == 201:
                service_logger.info('[CONSOLE] - Add Component success: [%s] [%s]' % (
                    data['name'], data['code']))
            elif r.json()['description'] == 'Code already exists':
                service_logger.warning(
                    '[CONSOLE] - Code already exists, Ignored. [%s] [%s]' % (data['name'], data['code']))
            else:
                service_logger.warning('[CONSOLE] - Add Component failed: [%s] [%s] response: [%s]' % (
                    data['name'], data['code'], r.json()))

        service_logger.info('[CONSOLE] > [Finished] Create component.')

        service_logger.info('[CONSOLE] > [Start] Associcate component with scopes')
        scopResult = self.s.get(url=self.clusterConsole +
                                scopeUri, verify=False).json()['scopes']
        componentResult = self.s.get(url=self.clusterConsole +
                                     componentUri, verify=False).json()['components']
        resourceList = self.s.get(
            url=self.clusterConsole+reousrceUrl, verify=False).json()['resources']

        scopeDic = {}
        componentDic = {}

        for scop in scopResult:
            if scop['children'] == None:
                scopeDic[scop['name']] = scop['uuid']
                service_logger.info('[CONSOLE] Found scops uuid: [%s][%s]' % (
                    scop['uuid'], scop['name']))
            elif scop['children'] != None:
                for child in scop['children']:
                    scopeDic[child['name']] = child['uuid']
                    service_logger.info('[CONSOLE] Found [%s] child scops uuid: [%s][%s]' % (
                        scop['name'], child['uuid'], child['name']))

        for com in componentResult:
            componentDic[com['name']] = com['uuid']

        componentUUID = None
        for res in resourceList:
            if res['code'] == 'COMPONENT':
                componentUUID = res['uuid']

        if componentUUID != None:
            componentUri = '%sapi/console/system/resources/%s/scopeMappings' % (
                self.clusterConsole, componentUUID)
            mapingDic = {
                "data": []
            }

            for j in jsonData:
                dicTmp = {
                    "rid": "",
                    "scopeUUIDs": []
                }
                comUuid = componentDic[j['name']]
                dicTmp['rid'] = comUuid
                service_logger.info('[CONSOLE] > Prepare compt: [%s]' % (j['name']))
                for scope in j['scopes']:
                    service_logger.info('[CONSOLE] - Prepare scope: [%s]' % (scope))
                    scopeUuid = scopeDic[scope]
                    dicTmp['scopeUUIDs'].append(scopeUuid)
                mapingDic['data'].append(dicTmp)

            r = self.s.put(url=componentUri, verify=False, json=mapingDic)
            service_logger.info('[CONSOLE] > [Finished] Associcate component with scopes')
            # print(mapingDic)

    def addMenus(self):
        menusUri = '/api/console/menus'
        componentUri = '/api/console/components'
        menusPath = '%sconsole_configs/menus.json' % self.baseconfPath
        jsonData = json.load(
            open(menusPath, mode='rt', encoding='utf-8'))

        for j in jsonData:
            data = {
                'name': j['name'],
                'path': j['path']
            }
            r = self.s.post(url=self.clusterConsole +
                            menusUri, verify=False, data=data)

            if r.status_code == 201:
                service_logger.info('[CONSOLE] > Add menu success: [%s], route: [%s]' % (
                    data['name'], data['path']))
            elif r.status_code == 400 and r.json()['description'] == 'Path already exists':
                service_logger.warning(
                    '[CONSOLE] - Path already exists, Ignored. [%s] [%s]' % (data['name'], data['path']))
            else:
                service_logger.error('[CONSOLE] - Add menu failed: [%s] [%s] response: [%s]' % (
                    data['name'], data['path'], r.json()))

        menusResult = self.s.get(
            url=self.clusterConsole+menusUri, verify=False).json()['menus']
        componentResult = self.s.get(
            url=self.clusterConsole+componentUri, verify=False).json()['components']

        componentDic = {}
        for component in componentResult:
            componentDic[component['name']] = component['uuid']

        menusDic = {}
        for menu in menusResult:
            menusDic[menu['name']] = menu['uuid']
        for j in jsonData:
            if j['components'] == []:
                service_logger.info('[CONSOLE] > Menu: [%s][%s] do NOT have components. Ignored.' % (
                    j['name'], j['path']))
            else:
                comList = []
                comNameList = []
                for com in j['components']:
                    comUuid = componentDic[com['name']]
                    comList.append(comUuid)
                    comNameList.append(com['name'])
                menusUuid = menusDic[j['name']]
                menuComponentUri = '/api/console/menus/%s/components' % menusUuid
                componentUUIDs = {'componentUUIDs': comList}
                r = self.s.put(url=self.clusterConsole+menuComponentUri,
                               verify=False, data=componentUUIDs)
                if r.status_code == 200:
                    service_logger.info(
                        '[CONSOLE] - Add component to menu success: menu[%s], component: %s' % (j['name'], comNameList))
                else:
                    service_logger.error('[CONSOLE] - Add menu failed: menu[%s], component: [%s], response: [%s]' % (
                        j['name'], comNameList), r.json())


    def usernameToUuid(self, emailAddress):
        urlListUrl = 'api/console/system/users'
        getUserListUrl = self.clusterConsole + urlListUrl

        r = self.s.get(url=getUserListUrl, verify=False)

        for u in r.json()['users']:
            if u['username'] == emailAddress:
                return u['uuid']

    def createTestProject(self):
        service_logger.info('Creating test project "%s"' % self.smoketestProject)
        # projectsUri = '/api/console/system/internal/general/projects'
        # r = self.s.get(self.clusterConsole + projectsUri).json()['projects']
        # for i in r:
        #     if i['name'] == '路测':
        #         adminRoleUUID = i['adminRoleUUID']

        createProjectUri = '/api/console/system/groups'
        needcreate = True
        r = self.s.get(url=self.clusterConsole + createProjectUri)
        if r.json()['groups'] == None:
            needcreate = True
        else:
            for project in r.json()['groups']:
                if project['name'] == self.smoketestProject:
                    self.smoketestProjectUuid = project['uuid']
                    needcreate = False
                    break

        if needcreate == True:
            # need create smoketest project.
            data = {
                'name': self.smoketestProject,
                # 'parentUUID': adminRoleUUID,
                'scenario': 'project'
            }
            r = self.s.post(url=self.clusterConsole +
                            createProjectUri, json=data)
            if r.json()['message'] == 'SUCCESS':
                self.smoketestProjectUuid = r.json()['group']['uuid']

                service_logger.info('Project UUID: ' + self.smoketestProjectUuid)
                service_logger.info(
                    'create test project "%s" successed.' % self.smoketestProject)
            else:
                service_logger.error('create test project "%s" failed.' % self.smoketestProject)
        else:
            # needcreate == False
            service_logger.info('"%s" project existed, ignore create.' % self.smoketestProject)

        projectRoleUri = '/api/console/system/groups/%s/roles' % self.smoketestProjectUuid
        r = self.s.get(self.clusterConsole+projectRoleUri).json()['roles']

        for role in r:
            if role['name'] == 'Admin':
                projectAdminRoleUuid = role['uuid']

        # projectAdminRoldCpntUuidDic = {
        #     "roleUUID": projectAdminRoleUuid,
        #     "rids": self.compunentsUuidList
        # }

        # projectRoleComponentsUri = '/api/console/system/batch/groups/%s/roles/resources/COMPONENT' % self.smoketestProjectUuid

        # r = self.s.get(self.clusterConsole +
        #                projectRoleComponentsUri).json()['rolesResources']
        # PrepareRolesResources = []
        # for res in r:
        #     if res['roleUUID'] == "" or res['roleUUID'] ==None:
        #         service_logger.info('Ignore Null roldUUID')
        #     elif res['roleUUID'] == projectAdminRoleUuid:
        #         PrepareRolesResources.append(projectAdminRoldCpntUuidDic)
        #     else:
        #         PrepareRolesResources.append(res)

        # data = {
        #     "rolesResources": PrepareRolesResources
        # }

        # r = self.s.put(self.clusterConsole +
        #                projectRoleComponentsUri,json=data)

        # if r.json()['message'] == 'SUCCESS':
        #     service_logger.info('Attach components to project role SUCCESS!')
        # else:
        #     service_logger.error('Attach components to project role Failed! res: %s' % (r.json()))

        self.adminUuid = self.usernameToUuid(emailAddress='admin')
        # self.smoketestUserUuid = self.usernameToUuid(
        #     emailAddress='smoketest@uisee.com')

        projectMemberUri = '/api/console/system/groups/%s/members' % self.smoketestProjectUuid
        admindata = {
            'userUUIDs': self.adminUuid,
            'roleUUIDs': projectAdminRoleUuid
        }
        # smkdata = {
        #     'userUUIDs': self.smoketestUserUuid,
        #     'roleUUIDs': projectAdminRoleUuid
        # }
        r = self.s.post(self.clusterConsole + projectMemberUri, data=admindata)
        service_logger.info('Attach "admin" user to project.')
        # r = self.s.post(self.clusterConsole + projectMemberUri, data=smkdata)
        # Attach "admin" && "smoketest@uisee.com" to smoketestProject.

        projectRolesUri = '/api/console/system/groups/%s/roles' % self.smoketestProjectUuid
        r = self.s.get(url=self.clusterConsole+projectRolesUri).json()['roles']

        existedProjectRole = {}

        for role in r:
            # Collect existed project role.
            existedProjectRole[role['name']] = role['uuid']

        self.smoketestPath = f'{sys.argv[3]}/console_configs/'

        yfile = yaml.round_trip_load(
            open(self.smoketestPath+'projectRoles.yaml', mode='rt').read())
        for role in yfile['consoleTestProjectRole']:
            for roleName, roleContent in role.items():
                if roleName in existedProjectRole:
                    service_logger.info(
                        'Project role existed, ignore create it: %s' % roleName)
                else:
                    data = {
                        'name': roleName
                    }
                    r = self.s.post(url=self.clusterConsole +
                                    projectRolesUri, json=data)
                    if r.json()['message'] == 'SUCCESS':
                        service_logger.info('Add project role %s SUCCESS!' %
                                    (roleName))
                    else:
                        service_logger.error('Add project role %s failed! res: %s' % (
                            roleName, r.json()))

        r = self.s.get(url=self.clusterConsole+projectRolesUri).json()['roles']

        existedProjectRole = {}
        existedProjectRoleN2I = {}
        for role in r:
            # Collect existed project role again.
            existedProjectRole[role['uuid']] = role['name']
            existedProjectRoleN2I[role['name']] = role['uuid']

        service_logger.info("Existed project role: %s" % existedProjectRoleN2I)


        # Import role detail options:
        for role in yfile['consoleTestProjectRole']:
            for roleName, roleContent in role.items():
                roleUuid = existedProjectRoleN2I[roleName]
                roleDetailUrl = '/api/console/system/groups/%s/roles/%s/resources' % (
                    self.smoketestProjectUuid, roleUuid)
                for rcode in roleContent['detail']:
                    service_logger.info('[Smoketest Project] Edit role "Detail": [%s] item.' % (roleName))
                    if roleContent['detail'][rcode].__len__() !=0:
                        data = {
                            'rcode': rcode,
                            'rids': roleContent['detail'][rcode][0]
                        }
                        roldDetailResult = self.s.post(self.clusterConsole +
                            roleDetailUrl, data=data).json()
                        if 'already' in roldDetailResult['description']:
                            service_logger.warn(
                                '[Smoketest Project] Role "detail" option ignored: %s, payload: %s' % (roldDetailResult['description'],data))
                        elif roldDetailResult['message'] == 'SUCCESS':
                            service_logger.info(
                                '[Smoketest Project] Role "detail" option correct: %s, payload: %s' % (roldDetailResult,data))
                        else:
                            service_logger.error(
                                '[Smoketest Project] Role "detail" option setting failed: %s ,payload: %s' % (roldDetailResult,data))
                    else:
                        service_logger.info(
                                '[Smoketest Project] Edit role "Detail": [%s], none detail item.' % (roleName))
        # Project global Resource enable:
        projectGlobalResourceUri = '/api/console/system/groups/%s/universeResourceCodes' % (self.smoketestProjectUuid)
        resourceList = ['CATEGORY','MAP','VEHICLE']
        for globalres in resourceList:
            data={'rcode': globalres}
            projectGlobalResourceResult = self.s.post(self.clusterConsole +projectGlobalResourceUri, json=data).json()

            if 'already' in roldDetailResult['description']:
                service_logger.warn(
                    '[Smoketest Project] project global resource enable ignored: %s, payload: %s' % (projectGlobalResourceResult['description'],data))
            elif projectGlobalResourceResult['message'] == 'SUCCESS':
                service_logger.info(
                    '[Smoketest Project] project global resource enabled: %s, payload: %s' % (projectGlobalResourceResult,data))
            else:
                service_logger.error(
                    '[Smoketest Project] project global resource setting failed: %s ,payload: %s' % (projectGlobalResourceResult,data))

        #Attach components to project user role
        menussUri = '/api/console/menus'
        self.menusResult = self.s.get(self.clusterConsole + menussUri).json()['menus']
        projectRoleComponentsUri = '/api/console/system/batch/groups/%s/roles/resources/COMPONENT' % self.smoketestProjectUuid

        r = self.s.get(self.clusterConsole +
                       projectRoleComponentsUri).json()['rolesResources']
        PrepareRolesResources = []
        for res in r:
            if res['roleUUID'] == "" or res['roleUUID'] == None:
                service_logger.info('Ignore Null roldUUID')
                continue

            roleN = existedProjectRole[res['roleUUID']]
            if roleN == 'Admin' or roleN == 'Member':
                service_logger.info('Ignore add menus to %s' % roleN)
                PrepareRolesResources.append(res)
                continue

            for role in yfile['consoleTestProjectRole']:
                for roleName, roleContent in role.items():
                    if roleN == roleName:
                        resItem = {"roleUUID": res['roleUUID'],
                                   "rids": []}
                        service_logger.info('> Prepare roleName: %s ' % roleName)
                        for ridName in roleContent['menus']:
                            service_logger.info('- Prepare parent rid: %s ' % ridName)
                            for menu in self.menusResult:
                                if ridName == menu['name']:
                                    for cmpt in roleContent['menus'][ridName]:
                                        # service_logger.info('· Prepare component: %s' % cmpt)
                                        for c in menu['components']:
                                            if cmpt == c['name']:
                                                resItem['rids'].append(
                                                    c['uuid'])
                        PrepareRolesResources.append(resItem)
        # print(PrepareRolesResources)
        # import json
        # print(json.dumps(PrepareRolesResources,ensure_ascii=False))
        data = {
            "rolesResources": PrepareRolesResources
        }

        projectRoleComponentsUri = '/api/console/system/batch/groups/%s/roles/resources/COMPONENT' % self.smoketestProjectUuid
        r = self.s.put(self.clusterConsole +
                       projectRoleComponentsUri, json=data).json()

        if r['message'] == 'SUCCESS':
            service_logger.info(
                '[Smoketest Project] Attach components to project user role SUCCESS!')
        else:
            service_logger.error(
                '[Smoketest Project] Attach components to project user role failed.: %s' % (r))
            service_logger.info(data)

    def createUpstreams(self):
        service_logger.info('Creating test Upstreams')
        upstreamsUri = '/api/console/notification/upstreams'
        # self.upstreamsResult = self.s.get(self.clusterConsole + upstreamsUri).json()['upstreams']

        upstreamsNeedCreate = True
        # if self.upstreamsResult != None:
        #     for upstreams in self.upstreamsResult:
        #         if upstreams['code'] == 'NOME':
        #             upstreamsNeedCreate = False

        if upstreamsNeedCreate == True:
            data = {"name":"NOME服务",
            "type":"service",
            "code":"NOME",
            "source":"cloud-nome-latest"}
            r = self.s.post(self.clusterConsole + upstreamsUri,data=data).json()
            service_logger.info('Create upstram: %s' % r['message'])

            upstreamUuid = r['upstream']['uuid']
            notifyconfigUri = '/api/console/notification/upstreams/%s/notifyConfigs' % upstreamUuid

            data={"channel":"MQTT_WS",
            "address":"/notifications/nome",
            "objectType":"ALL",
            "retryMaxTimes":0,
            "retryIntervalMs":None}

            r = self.s.post(self.clusterConsole + notifyconfigUri,data=data).json()
            service_logger.info('Create notifyconfig: %s' % r['message'])
        else:
            service_logger.info('NOME upstream existed, ignore create')



myConsole = ConsoleImporter()
myConsole.addResource()
myConsole.addService()
myConsole.addScope()
myConsole.associateScope()
myConsole.addMenus()
myConsole.createTestProject()
myConsole.createUpstreams()