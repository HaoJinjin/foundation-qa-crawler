# 快速开始指南 

---

## 1、前期的安装工作（必做） 🔧

1. 安装 Node.js（用于前端）
   - 推荐安装 LTS 版本（例如 Node 24.12.0）：https://nodejs.org/
   ![图片](public\QQ20260203-211437.png)
   - Windows 用户：下载 MSI 安装包并一路 "下一步" 即可。
   - 验证：在命令行运行：
     ```bash
     node -v
     npm -v
     ```
     ![图片](public\e1aaeecc05d96a998c20c49e4466d6e0.png)

2. 安装 Python（用于后端）跳过

3. 安装 VS Code 中常用的vue扩展：
   ![图片](public\QQ20260203-210549.png)
   

---

## 2、安装依赖（前端） ✅

### 前端（Node.js）
```bash
# 项目根目录（含 package.json）
# 安装依赖（使用 npm）
npm install
```

---

## 3、启动前端 + 后端 ▶️

### 启动后端服务
```bash
cd backend
# 启动（示例）：
python main.py
```
预期输出（示例）：
```
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     Application startup complete
```


### 启动前端开发服务器
```bash
# 项目根目录
npm run dev
```
预期输出（示例）：
```
  VITE vX.X.X  ready in XXX ms
  Local: http://localhost:5173/
```

在浏览器打开上面地址，应该能看到前端页面并与后端接口交互。

---

## 4、前端项目结构 🗂️

项目中的前端相关文件位于 `src/` 与 `public/`：

- `public/`
  - 静态资源（图片、favicon 等），可以在代码中用 `/文件名` 访问。
  - 例如本项目放了一张截图：`public/QQ20260203-210549.png`，在 Markdown 或页面中用 `/QQ20260203-210549.png` 引用。

- `src/main.ts`：应用入口，挂载 Vue、注册路由与 store。
- `src/App.vue`：根组件，所有页面的外层容器。
- `src/pages/`：每个页面都在这里（`Dashboard.vue`, `Trends.vue`, `Users.vue`, `Content.vue`, `DataTable.vue`）。
- `src/components/`：可复用小组件（例如图表、卡片）。
- `src/api/client.ts`：与后端交互的集中封装（请求封装、错误处理）。
- `src/stores/useDataStore.ts`：Pinia 状态管理（保存数据、封装数据获取方法）。
- `vite.config.ts`：Vite 的配置，包含别名、代理等（开发时可配置代理将前端请求转发到后端）。

![图片](public\fb22de32613187486ff1efe51837f63c.png)
---
