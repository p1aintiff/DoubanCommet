## 路径

1. 电影排行榜，获取分类及其链接
   **来源**
   https://movie.douban.com/chart
   `div.aside>div>div.types>a`
   获取文本
   及其href属性 https://movie.douban.com/typerank?type_name=%E5%89%A7%E6%83%85&type=11&interval_id=100:90&action=
   **储存**
   typename: 剧情
   type: 11

2. 获取所有电影简单信息
   使用type 对应的id可以直接遍历
   经检验，第一步的id不全；可以直接遍历 1-31
   在href后面拼接`&start=0&limit=20`可以获取指定数量电影
   https://movie.douban.com/j/chart/top_list?type=11&interval_id=100%3A90&action=&start=20&limit=20

   拿到所有电影普通json，用来提取url
   **储存**
   电影细节（名字，url）

3. 单部电影细节信息
    1. 电影url 到 json-ld
      json 补充到电影细节
    2. url 到评论
       `https://movie.douban.com/subject/2998451/comments?percent_type=&start=0&limit={amount}&status=P&sort=new_score&comments_only=1`
         
    评论表（电影url，昵称，昵称url，。。。。）