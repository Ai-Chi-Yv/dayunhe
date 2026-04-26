# 后端启动说明

## 目录中的文件
- `app.py`：Flask 后端
- `requirements.txt`：依赖
- `京杭大运河_游客导览增强版_三次修改.html`：你的前端页面

## 运行步骤

```bash
pip install -r requirements.txt
python app.py
```

启动后打开：

```text
http://127.0.0.1:5000/
```

## 接口

- `GET /api/health`：健康检查
- `GET /api/stats`：路线统计
- `GET /api/stops`：全部站点
- `GET /api/stops/<name>`：按站点名获取详情
- `GET /api/current?idx=0`：获取当前站点
- `GET /api/search?q=苏州`：搜索站点

## 说明

这个后端会直接读取你当前 HTML 里的 `const stops = [...]` 数据，所以前端改了，后端数据也会同步。
