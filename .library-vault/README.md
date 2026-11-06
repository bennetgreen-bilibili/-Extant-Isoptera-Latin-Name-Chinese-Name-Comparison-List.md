# 文库加密备份（.library-vault/）

本目录是「_unpublished/文库/」的**加密快照**，用于把本地文库备份到 GitHub。
文库原文（书 + 论文全文）仍在 _unpublished/ 下，被 .gitignore 排除；这里只有密文。

## 恢复

    # 1) 准备密钥（不进仓库；口令由你保管，例如密码管理器）
    printf '%s
' '你的口令' > _tmp/vault.key

    # 2) 校验并解包到 _unpublished/文库
    python _tools/library_vault.py unpack --key-file _tmp/vault.key

默认拒绝写入非空目录；在新机器上恢复时先 git clone，mkdir -p _unpublished，再 unpack。
--target DIR 可解到别处，--force 才覆盖已有文件。

## 结构

    .library-vault/
      manifest.json    KDF 参数、salt、iv、HMAC、明文/密文 sha256、分块清单
      part-000.bin …   密文分块（默认每块 24 MB，低于 GitHub 单文件 100 MB 硬限）

格式：library.tar.gz → AES-256-CTR（scrypt 派生 64 字节，前 32 字节加密、后 32 字节 HMAC）→
encrypt-then-MAC（HMAC-SHA256 覆盖全部密文）→ 切块。
unpack 会先核对每块 sha256、整段 sha256 和 HMAC，任何一项不符都拒绝解密。

## 边界（请如实理解）

- 这层加密防的是「仓库被随手浏览 / 爬虫和搜索引擎 / DMCA 扫描命中」，**不是法律盾牌**：
  版权仍属原作者与出版方，仅限个人研究备份，不得再分发。
- 口令若很弱（单词、短句），拿到仓库的人可以离线爆破；scrypt(n=16384, r=8, p=1)
  只是提高了每次尝试的成本，不是不可破。
- **密钥丢失 = 备份报废**。密钥不能提交进仓库（提交了就等于没加密）。
- 重新 pack 会整体替换分块与 manifest；旧快照仍留在 git 历史里。
