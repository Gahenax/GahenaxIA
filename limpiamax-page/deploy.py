import os
import paramiko
from pathlib import Path


SFTP_HOST = os.environ['SFTP_HOST']
SFTP_PORT = int(os.environ.get('SFTP_PORT', 22))
SFTP_USER = os.environ['SFTP_USER']
SFTP_PASS = os.environ['SFTP_PASS']

LOCAL_DIR = Path('out')
REMOTE_DIR = 'public_html'


def upload_dir(sftp, local_dir: Path, remote_dir: str):
    try:
        sftp.mkdir(remote_dir)
    except OSError:
        pass
    for item in sorted(local_dir.iterdir()):
        remote_path = f'{remote_dir}/{item.name}'
        if item.is_dir():
            upload_dir(sftp, item, remote_path)
        else:
            print(f'  {item} -> {remote_path}')
            sftp.put(str(item), remote_path)


transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
transport.connect(username=SFTP_USER, password=SFTP_PASS)
sftp = paramiko.SFTPClient.from_transport(transport)

try:
    print(f'Deploying {LOCAL_DIR}/ to {REMOTE_DIR}/ on {SFTP_HOST}...')
    upload_dir(sftp, LOCAL_DIR, REMOTE_DIR)
    print('Deployment complete!')
finally:
    sftp.close()
    transport.close()
