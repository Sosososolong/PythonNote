from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client

class FDFSStorage(Storage):
    """FastDFS文件存储类"""
    def __init__(self, client_conf=None, base_url=None):
        """初始化, 使用FastDFS的python包, 需要指定一个配置文件(tracker server的位置等信息), 和还有storage server的地址, 用于前端访问下载文件
        这两个参数都放到了settings.py配置文件中配置, 这里导入settings即可使用"""
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        """打开文件时使用"""
        pass

    def _save(self, name, content):
        """保存文件时使用"""
        # name: 上传文件的名字
        # content: 包含需要上传文件的File类的一个对象

        # 创建一个Fdfs_client对象, 程序通过client.conf文件去找FastDFS的tracker server
        client = Fdfs_client(self.client_conf)
        # linux中pip install py3Fdfs 后, 网上说使用这种方式创建Fdfs_client对象
        # tracker_path = get_tracker_conf(self.client_conf)
        # client = Fdfs_client(tracker_path)

        # 上传文件到FastDFS系统中
        res = client.upload_by_buffer(content.read())
        # res
        # {
        #     'Group name'      : group_name,
        #     'Remote file_id'  : remote_file_id,
        #     'Status'          : 'Upload successed.',
        #     'Local file name' : '',
        #     'Uploaded size'   : upload_size,
        #     'Storage IP'      : storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到FastDFS失败')

        # 获取返回的文件id
        filename = res.get('Remote file_id')

        return filename

    def exists(self, name):
        """Django判断文件名是否可用, True表示文件已经存在, 就不会上传, 由于我们这里会将文件叫由FastDFS管理,
        FastDFS会处理文件名重复等问题, 所以此方法返回False即可"""
        return False

    # 使用Django默认的后台管理系统上传图片就可以正常的使用FastDFS保存文件了,保存一个文件后,
    # Django将会拿到文件的id(类似"/group1/M00/00/00/wKgBb14O4iuAEQoAAADN85_Jt5s945.jpg")存储到数据库中商品表的image字段,
    # 所以前端显示图片的时候图片地址直接填 "goods.image"是不对的, 如果填 "goods.image.url" 就会调用此函数, 在此函数中做好
    # 图片正确地址的拼接返回即可
    def url(self, name):
        """返回访问文件的url路径, name就是文件保存到storage server里面的文件id(文件名)"""
        return self.base_url + name
