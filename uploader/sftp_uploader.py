import os
from yaml import load
import paramiko
import stat

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader

from .upload_exception import UploadException


class DirSFTPClient(paramiko.SFTPClient):

    def rm_dir(self, target):
        for item in self.listdir(target):
            item_path = os.path.join(target, item)
            item_stat = self.lstat(item_path)
            if stat.S_ISREG(item_stat.st_mode):
                self.remove(item_path)
            elif stat.S_ISDIR(item_stat.st_mode):
                self.rm_dir(item_path + '/')
                self.rmdir(item_path + '/')

    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), f'{target}/{item}')
            else:
                self.mkdir(f'{target}/{item}', ignore_existing=True)
                self.put_dir(os.path.join(source, item), f'{target}/{item}')

    def mkdir(self, path, mode=511, ignore_existing=False):
        try:
            super(DirSFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


class SFTPUploader:

    @staticmethod
    def check_configuration(cfg):
        entries = cfg['upload'].keys()
        if 'host' not in entries:
            raise UploadException('Host not found in upload configuration')
        if 'port' not in entries:
            raise UploadException('Port not found in upload configuration')
        if 'path' not in entries:
            raise UploadException('Path not found in upload configuration')
        if 'user' not in entries:
            raise UploadException('User not found in upload configuration')
        if 'password' not in entries:
            raise UploadException('Password not found in upload configuration')

    @staticmethod
    def upload():
        if not os.path.exists('site'):
            raise UploadException('Site does not exist. Build the site first')
        if not os.path.exists('data/upload.yaml'):
            raise UploadException('Upload configuration not found')
        with open('data/upload.yaml', 'r') as config_file:
            cfg = load(config_file.read(), Loader=Loader)
        if cfg is None:
            raise UploadException('Invalid configuration')
        SFTPUploader.check_configuration(cfg)
        print('Connecting to SFTP...', end=' ')
        transport_params = (
            cfg['upload']['host'],
            int(cfg['upload']['port'])
        )
        transport = paramiko.Transport(sock=transport_params)
        transport.connect(
            username=cfg['upload']['user'],
            password=cfg['upload']['password']
        )
        sftp = DirSFTPClient.from_transport(transport)
        print('Connected!')
        print('Deleting current remote files...', end=' ')
        sftp.rm_dir(cfg['upload']['path'])
        print('Completed!')
        for item in os.listdir('site/'):
            print(f'Transferring {item}', end=' ')
            if item == '.htaccess' and cfg['upload']['upload_htaccess'].lower() != 'true':
                print('[SKIPPED]')
                continue
            realpath = os.path.join('site/', item)
            targetpath = os.path.join(cfg['upload']['path'], item)
            if os.path.isdir(realpath):
                print('[DIR]',)
                sftp.mkdir(targetpath)
                sftp.put_dir(realpath, targetpath)
            elif os.path.isfile(realpath):
                print('[FILE]...', end=' ')
                sftp.put(realpath, targetpath)
                print('Completed!')
            else:
                print('[IGNORED]')
        print('Upload complete!')
        if sftp:
            sftp.close()
        if transport:
            transport.close()
