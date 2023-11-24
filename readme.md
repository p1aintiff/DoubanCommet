## 路径

1. 电影排行榜，获取分类及其链接  
   **来源**  
   - `https://movie.douban.com/chart`  
   - css：`div.aside>div>div.types>a`  
   - 文本提取分类名，href中提取出id
   - **储存**  
     - typename: 剧情  
     - type: 11
   >目前id有1-31,可以直接遍历
   
2. 获取所有电影简单信息
   - 在href后面拼接`&start=0&limit=20`可以获取指定数量电影
   - `https://movie.douban.com/j/chart/top_list?type={这里填id}&interval_id=100%3A90&action=&start=20&limit=20`  
   - 每一个分类链接中，有很多电影，综合各种分类，可以获取所有电影
  
3. 单部电影细节信息  
   - 电影url 到 json-ld  
      > 可以直接加入到mongo
   - url 后拼接以下  
       `comments?percent_type=&start=0&limit={评论的数量}&status=P&sort=new_score&comments_only=1`
   > 目前数量600条，type有空，h,m,l
   
4. 其他设置
   - 代理ip
   - 并发数
   - ua