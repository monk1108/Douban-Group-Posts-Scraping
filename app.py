from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<table_name>')
def display_table(table_name):
    # 连接数据库
    conn = sqlite3.connect('douban_posts.db')
    cursor = conn.cursor()
    
    # 查询数据库
    sql = f"SELECT id, article, contents, replys, url FROM {table_name}_content"
    cursor.execute(sql)
    records = cursor.fetchall()
    
    # 关闭数据库连接
    conn.close()

    # 确定页面标题
    page_titles = {
        'homdi': 'HOMDI',
        'lyd': 'LYD',
        'yuzhi_wang': 'YUZHI',
        'wakin': 'WAKIN',
        'wakin_chau': 'WakinChau'
    }
    page_title = page_titles.get(table_name, '豆瓣小组帖子')

    # 渲染模板并传递查询结果和页面标题
    return render_template('table.html', records=records, page_title=page_title)

if __name__ == '__main__':
    app.run(debug=True)
