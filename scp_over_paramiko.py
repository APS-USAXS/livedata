# usage: http://stackoverflow.com/questions/250283/how-to-scp-in-python

import paramiko
from scp import SCPClient

def createSSHClient(server, port=None, user=None, password=None):
    '''ssh over a paramiko transport'''
    # see: http://stackoverflow.com/questions/250283/how-to-scp-in-python
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #client.connect(server, port, user, password)
    client.connect(server, username=user)
    return client


def demo():
    '''show a scp transaction'''
    server = 'www-i.xray.aps.anl.gov'
    user = 'usaxs'
    ssh = createSSHClient(server, user=user)
    scp = SCPClient(ssh.get_transport())
    scp.put('README', remote_path='www/livedata')


if __name__ == '__main__':
    demo()
