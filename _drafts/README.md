# _drafts —— 初稿文件夹（不会被发布）

这里放还没定稿的文章。Jekyll 默认**不构建** `_drafts/`（除非用 `jekyll build --drafts`），
所以放在这里的文件可以直接提交进仓库，不会出现在 /blog/ 列表里，也不会被站点地图收录。

## 定稿流程

1. 把 `_drafts/xxx.md` 移动到 `_posts/`。
2. 文件名改成 `YYYY-MM-DD-标题.md`（日期用发布日期）。
3. 在 front matter 里补一行 `date: YYYY-MM-DD 00:00:00 +0800`。
4. 推送到 main，GitHub Actions 会自动构建并部署。

`_posts` 的默认 front matter（layout: post、author、lang、permalink）在 `_config.yml` 的 defaults 里，
移到 `_posts` 之后这些字段可以省略；权限与合规相关内容按需自加。

## 注意

- 文件名不要用半角冒号 `:`，Windows 不允许；中文全角「：」可以，但建议统一用 `-`。
- `_posts` 里的日期决定排序，博客列表按日期倒序。
