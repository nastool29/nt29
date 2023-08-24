import os.path

import ruamel

from app.utils import StringUtils, ExceptionUtils, PathUtils
from app.utils.commons import singleton
from config import Config


@singleton
class IndexerHelper:
  _indexers = []

  def __init__(self):
    self.init_config()

  def init_config(self):
    try:
      # 读取明文配置文件(取代sites.dat)
      _indexers = []
      _site_path = Config().get_sites_path()
      cfg_files = PathUtils.get_dir_files(in_path=_site_path, exts=[".yml"])
      for cfg_file in cfg_files:
        with open(cfg_file, mode='r', encoding='utf-8') as f:
          print(cfg_file)
          _indexers.extend(ruamel.yaml.YAML().load(f))
      self._indexers = _indexers
    except Exception as err:
      ExceptionUtils.exception_traceback(err)
    self.get_all_public_indexers()

  def get_all_indexers(self):
    return self._indexers

  def get_all_public_indexers(self):
    """
    获取所有的公开站点，并返回字段
    :return: 公开站点的字典
    """
    _public_site = {}
    for _indexer in self._indexers:
      if 'public' in _indexer and _indexer['public']:
        _, netloc = StringUtils.get_url_netloc(_indexer.get("domain"))
        _public_site[netloc] = _indexer
    return _public_site

  def get_indexer(self,
      url,
      cookie=None,
      name=None,
      rule=None,
      public=None,
      proxy=False,
      parser=None,
      ua=None,
      render=None,
      language=None,
      pri=None):
    if not url:
      return None
    for indexer in self._indexers:
      if not indexer.get("domain"):
        continue
      if StringUtils.url_equal(indexer.get("domain"), url):
        return IndexerConf(datas=indexer,
                           cookie=cookie,
                           name=name,
                           rule=rule,
                           public=public,
                           proxy=proxy,
                           parser=parser,
                           ua=ua,
                           render=render,
                           builtin=True,
                           language=language,
                           pri=pri)
    return None


class IndexerConf(object):

  def __init__(self,
      datas=None,
      cookie=None,
      name=None,
      rule=None,
      public=None,
      proxy=False,
      parser=None,
      ua=None,
      render=None,
      builtin=True,
      language=None,
      pri=None):
    if not datas:
      return
    # ID
    self.id = datas.get('id')
    # 名称
    self.name = datas.get('name') if not name else name
    # 是否内置站点
    self.builtin = builtin
    # 域名
    self.domain = datas.get('domain')
    # 搜索
    self.search = datas.get('search', {})
    # 批量搜索，如果为空对象则表示不支持批量搜索
    self.batch = self.search.get("batch", {}) if builtin else {}
    # 解析器
    self.parser = parser if parser is not None else datas.get('parser')
    # 是否启用渲染
    self.render = render if render is not None else datas.get("render")
    # 浏览
    self.browse = datas.get('browse', {})
    # 种子过滤
    self.torrents = datas.get('torrents', {})
    # 分类
    self.category = datas.get('category', {})
    # Cookie
    self.cookie = cookie
    # User-Agent
    self.ua = ua
    # 过滤规则
    self.rule = rule
    # 是否公开站点
    self.public = public
    # 是否使用代理
    self.proxy = proxy
    # 仅支持的特定语种
    self.language = language
    # 索引器优先级
    self.pri = pri if pri else 0
