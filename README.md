# simple-search
基于  Redis 的简单中文搜索系统

# 开发环境
python 2.6.6/2.7.5 && centos

# 依赖
<em>如提示  Temporary failure in name resolution，请多试几次</em>

* pip install gevent (yum install python-devel)
* easy_install redis
* easy_install bottle
* easy_install bottle-redis

# 启动
nohup python main.py &

# 输入
curl -d "$data" http://xxx.com/set/$type/$info?score=$score

* 请确保输入内容字符集为 utf-8 类型
* $data 对搜索的内容进行分词，并把结果存入 redis
* $type 支持的类型，如文章、评论等，由此可用一个搜索服务提供不同类型结果
* $info 对应的内容表示，如文章ID，等
* $score 参考排序，默认使用当前时间戳

<em>批量输入请自行配置 input 目录下的脚本文件</em>

* nohup bash input.sh &
* \*/15 * * * * cd /root/search && bash input.sh >> update-search.log

# 输出
curl http://xxx.com/get/$type?query=$query

* $type 同输入
* $query 搜索关键字



