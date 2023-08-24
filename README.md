
![nt29](config/nt29.svg)


# nt29 媒体库管理工具
nt29 is a fork of nas-tools.

致敬nastools,nt29 以 nastools2.9.1为基础开发,感谢`jxxghp`大佬开发的 [nastools](https://github.com/NAStool/nas-tools).

API: http://localhost:3300/api/v1/


## 功能：

NAS媒体库管理工具。
默认账号密码：admin/password

## 安装
### 1、Docker
```
docker pull jxxghp/nas-tools:latest
```

如无法连接Github，注意不要开启自动更新开关(NASTOOL_AUTO_UPDATE=false)，将NASTOOL_CN_UPDATE设置为true可使用国内源加速安装依赖。

### 2、本地运行
python3.11版本，开发时使用poetry:1.5.1 python:3.11.4.如发现缺少依赖包需额外安装
#### 2.1、使用PyCharm
PyCharm setting->add interpreter->poetry environment ->python interpreter 使用poetry。
PyCharm 运行run.py即可,Environment variables 添加：NASTOOL_CONFIG=/xx/xx/config.yaml（注意多个参数使用分号隔开）
#### 2.2、使用命令行
```
poetry install
export NASTOOL_CONFIG="/xxx/config/config.yaml"
nohup python3 run.py & 
```
#### 2.3、Docker打包
docker打包最终使用的还是requirement【因为我不会Dockerfile配置】

### 3、nt29 变更点

* 使用poetry管理python依赖
* 升级python 3.11.x，开发时使用poetry:1.5.1 python:3.11.4

### 4、功能点入口
* indexer 查询入口：web/main.py @App.route('/indexer', methods=['POST', 'GET'])
* 【导航栏：资源搜索】： web/main.py @App.route('/search', methods=['POST', 'GET']) 
* 【头部：搜索框】 action.py function: __search(data) -> Searcher().search_medias -> indexer.search_by_keyword -> executor.sumbit(search) -> builtin.py: function search() -> __spider_search 
