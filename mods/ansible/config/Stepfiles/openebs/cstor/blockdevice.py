import yaml
import sys


local_path=sys.argv[1]

with open(f'{local_path}/cstor_pool_template.yaml','r') as y:
    cs=yaml.safe_load(y)

devices=[]
with open(f'{local_path}/blockdevice.txt','r') as f:
    block_device_list=f.readlines()
for block_device in block_device_list:
    block_name = block_device.strip().split(' ')
    temple = {
        'nodeSelector': {
            'kubernetes.io/hostname': block_name[1]
        },
        'dataRaidGroups': [
            {
                'blockDevices': [
                    {
                        'blockDeviceName':  block_name[0]
                    }
                ]
            }
        ],
        'poolConfig': {
            'dataRaidGroupType': 'stripe'
        }
    }

    devices.append(temple)
cs['spec']['pools']=devices

with open(f'{local_path}/cstor_pool.yaml','w') as y:
    yaml.safe_dump(cs,y)