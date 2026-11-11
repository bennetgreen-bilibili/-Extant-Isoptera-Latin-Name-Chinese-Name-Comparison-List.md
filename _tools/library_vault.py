#!/usr/bin/env python3
"""文库加密备份（.library-vault/）。

把 _unpublished/文库/ 打成一个 tar.gz，用 scrypt 派生密钥 + AES-256-CTR 加密，
再做 HMAC-SHA256（encrypt-then-MAC），最后切块写入 .library-vault/，便于提交到 GitHub。

密钥不进仓库：默认从 _tmp/vault.key（已 gitignore）读取，或用 --key-file / 环境变量
LIBRARY_VAULT_KEY。AES 由本机 openssl 命令行完成（Git for Windows 自带）。

用法：
    python _tools/library_vault.py pack      [--key-file _tmp/vault.key]
    python _tools/library_vault.py unpack    --key-file _tmp/vault.key [--target DIR] [--force]
    python _tools/library_vault.py verify    [--key-file _tmp/vault.key]
    python _tools/library_vault.py info

安全边界：
- 这层加密防的是「仓库被随手浏览 / 被搜索引擎、爬虫、DMCA 扫描命中」，不是法律盾牌；
- 口令弱（如单词）时，拿到仓库的人可以离线爆破，别把密文当机密文件保险箱；
- 密钥文件丢了 = 备份报废；请把它单独存进密码管理器。
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LIBRARY = ROOT / "_unpublished" / "文库"
DEFAULT_VAULT = ROOT / ".library-vault"
DEFAULT_KEY_FILE = ROOT / "_tmp" / "vault.key"
FORMAT = "dsh-library-vault/1"
SCRYPT = {"n": 16384, "r": 8, "p": 1, "dklen": 64}
PART_SIZE = 24_000_000  # 24 MB：低于 GitHub 100 MB 单文件硬限，也低于 50 MB 警告线


# ---------------------------------------------------------------- helpers

def die(msg):
    print("[vault] 错误：" + msg, file=sys.stderr)
    raise SystemExit(1)


def _openssl_works(exe):
    """Git for Windows 的 usr/bin/openssl.exe 是 MSYS 程序，在受限沙盒里会因

    "couldn't create signal pipe" 直接崩溃；ucrt64/bin 下的是原生程序，可用。
    所以路径存在还不够，得真跑一次 version。"""
    try:
        p = subprocess.run([str(exe), "version"], capture_output=True, timeout=30)
    except Exception:
        return False
    return p.returncode == 0


def find_openssl():
    exe = shutil.which("openssl") or os.environ.get("OPENSSL")
    candidates = [exe]
    # 从 git 的位置反推（Git 不在 C 盘时也能找到，如 E:\Program Files\Git）
    git = shutil.which("git")
    if git:
        root = Path(git).resolve().parent.parent
        candidates += [
            root / "ucrt64" / "bin" / "openssl.exe",
            root / "mingw64" / "bin" / "openssl.exe",
            root / "usr" / "bin" / "openssl.exe",
        ]
    candidates += [
        r"C:\Program Files\Git\ucrt64\bin\openssl.exe",
        r"C:\Program Files\Git\mingw64\bin\openssl.exe",
        r"C:\Program Files\Git\usr\bin\openssl.exe",
        "/usr/bin/openssl",
        "/usr/local/bin/openssl",
    ]
    for c in candidates:
        if c and Path(c).is_file() and _openssl_works(c):
            return str(c)
    die("找不到可用的 openssl（AES 由它完成）。装 Git for Windows 或设置 OPENSSL 环境变量。")


def read_key(args):
    if getattr(args, "key_file", None):
        p = Path(args.key_file)
        if not p.is_file():
            die("密钥文件不存在：" + str(p))
        key = p.read_text(encoding="utf-8").strip()
    else:
        key = os.environ.get("LIBRARY_VAULT_KEY", "").strip()
        if not key and DEFAULT_KEY_FILE.is_file():
            key = DEFAULT_KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        die("没有密钥。写一行口令进 _tmp/vault.key，或传 --key-file / 设置 LIBRARY_VAULT_KEY。")
    if len(key) < 6:
        die("口令太短（至少 6 个字符）。")
    return key


def derive_keys(passphrase, salt, params):
    dk = hashlib.scrypt(
        passphrase.encode("utf-8"), salt=salt,
        n=params["n"], r=params["r"], p=params["p"], dklen=params["dklen"],
        maxmem=params["n"] * params["r"] * 128 * 2,
    )
    return dk[:32], dk[32:64]


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def hmac_sha256(key, path):
    h = hmac.new(key, digestmod=hashlib.sha256)
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def make_workdir(prefix):
    base = ROOT / "_tmp" if (ROOT / "_tmp").is_dir() else Path(tempfile.gettempdir())
    while True:
        d = base / (prefix + uuid.uuid4().hex)
        try:
            os.makedirs(d)
            return d
        except FileExistsError:
            continue


def human(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d B" % n) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024
    return str(n)


def openssl_crypt(openssl, key, iv, src, dst, decrypt):
    cmd = [openssl, "enc", "-aes-256-ctr", "-K", key.hex(), "-iv", iv.hex(), "-nosalt",
           "-in", str(src), "-out", str(dst)]
    if decrypt:
        cmd.append("-d")
    proc = subprocess.run(cmd)
    if proc.returncode != 0 or not dst.is_file():
        die("openssl 失败（退出码 %s）" % proc.returncode)


# ---------------------------------------------------------------- pack

def build_tar_gz(library, out):
    files = 0
    with open(out, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for path in sorted(library.rglob("*"), key=lambda p: p.as_posix()):
                    if not path.is_file():
                        continue
                    rel = path.relative_to(library).as_posix()
                    info = tar.gettarinfo(str(path), arcname=rel)
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with open(path, "rb") as f:
                        tar.addfile(info, f)
                    files += 1
    return files, out.stat().st_size


def cmd_pack(args):
    library = Path(args.library)
    vault = Path(args.vault)
    if not library.is_dir():
        die("文库目录不存在：" + str(library))
    key = read_key(args)
    openssl = find_openssl()

    vault.mkdir(parents=True, exist_ok=True)
    work = make_workdir("vault-")
    try:
        plain = work / "library.tar.gz"
        print("[vault] 打包 tar.gz …")
        files, plain_bytes = build_tar_gz(library, plain)
        plain_sha = file_sha256(plain)

        salt = os.urandom(16)
        iv = os.urandom(16)
        enc_key, mac_key = derive_keys(key, salt, SCRYPT)
        cipher = work / "library.tar.gz.enc"
        print("[vault] AES-256-CTR 加密 " + human(plain_bytes) + " …")
        openssl_crypt(openssl, enc_key, iv, plain, cipher, decrypt=False)
        cipher_sha = file_sha256(cipher)
        mac = hmac_sha256(mac_key, cipher)
        cipher_bytes = cipher.stat().st_size

        part_size = args.part_size
        parts = []
        with open(cipher, "rb") as src:
            idx = 0
            while True:
                block = src.read(part_size)
                if not block:
                    break
                name = "part-%03d.bin" % idx
                p = vault / name
                p.write_bytes(block)
                parts.append({"name": name, "bytes": len(block),
                              "sha256": hashlib.sha256(block).hexdigest()})
                idx += 1
        _prune_old_parts(vault, set(p["name"] for p in parts))

        manifest = {
            "format": FORMAT,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "cipher": "aes-256-ctr+hmac-sha256",
            "kdf": {"alg": "scrypt", "salt": salt.hex(), "iv": iv.hex(), **SCRYPT},
            "mac": mac,
            "plain": {"file": "library.tar.gz", "bytes": plain_bytes, "sha256": plain_sha},
            "ciphertext": {"bytes": cipher_bytes, "sha256": cipher_sha},
            "parts": parts,
            "stats": {"files": files, "source_bytes": plain_bytes},
            "note": "密钥不进仓库。解包见 .library-vault/README.md；口令丢失 = 备份报废。",
        }
        mpath = vault / "manifest.json"
        tmp = mpath.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, mpath)
        _write_vault_readme(vault)

        total = sum(p["bytes"] for p in parts)
        print("[vault] 完成：%d 个文件 → %s → %d 块 / %s" % (files, human(plain_bytes), len(parts), human(total)))
        print("[vault] manifest: " + str(mpath))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _prune_old_parts(vault, keep):
    for p in vault.glob("part-*.bin"):
        if p.name not in keep:
            p.unlink()


VAULT_README = """# 文库加密备份（.library-vault/）

本目录是「_unpublished/文库/」的**加密快照**，用于把本地文库备份到 GitHub。
文库原文（书 + 论文全文）仍在 _unpublished/ 下，被 .gitignore 排除；这里只有密文。

## 恢复

    # 1) 准备密钥（不进仓库；口令由你保管，例如密码管理器）
    printf '%s\n' '你的口令' > _tmp/vault.key

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
"""


def _write_vault_readme(vault):
    path = vault / "README.md"
    if not path.exists():
        path.write_text(VAULT_README, encoding="utf-8")


# ---------------------------------------------------------------- verify / unpack

def load_manifest(vault):
    mpath = vault / "manifest.json"
    if not mpath.is_file():
        die("没有 manifest：" + str(mpath) + "（先 pack）")
    m = json.loads(mpath.read_text(encoding="utf-8"))
    if m.get("format") != FORMAT:
        die("manifest 格式不支持：" + str(m.get("format")))
    return m


def assemble_cipher(vault, m, dst):
    h_all = hashlib.sha256()
    with open(dst, "wb") as out:
        for part in m["parts"]:
            p = vault / part["name"]
            if not p.is_file():
                die("缺分块：" + str(p))
            data = p.read_bytes()
            if len(data) != part["bytes"] or hashlib.sha256(data).hexdigest() != part["sha256"]:
                die("分块校验失败：" + part["name"] + "（被改动或拷贝不完整）")
            out.write(data)
            h_all.update(data)
    if h_all.hexdigest() != m["ciphertext"]["sha256"]:
        die("整段密文 sha256 不符")


def cmd_verify(args):
    vault = Path(args.vault)
    m = load_manifest(vault)
    fd, name = tempfile.mkstemp(suffix=".enc")
    os.close(fd)
    tmp = Path(name)
    try:
        assemble_cipher(vault, m, tmp)
        print("[vault] 分块与整段 sha256 OK")
        if getattr(args, "key_file", None) or os.environ.get("LIBRARY_VAULT_KEY") or DEFAULT_KEY_FILE.is_file():
            key = read_key(args)
            enc_key, mac_key = derive_keys(key, bytes.fromhex(m["kdf"]["salt"]), m["kdf"])
            if not hmac.compare_digest(hmac_sha256(mac_key, tmp), m["mac"]):
                die("HMAC 不符：密钥不对，或密文被篡改")
            print("[vault] HMAC OK（密钥正确）")
        else:
            print("[vault] 未提供密钥，跳过 HMAC")
        return 0
    finally:
        tmp.unlink(missing_ok=True)


def cmd_unpack(args):
    vault = Path(args.vault)
    target = Path(args.target)
    key = read_key(args)
    m = load_manifest(vault)
    openssl = find_openssl()
    if target.exists() and any(target.iterdir()) and not args.force:
        die("目标目录非空：" + str(target) + "（用 --force 覆盖，或换 --target）")

    work = make_workdir("vault-restore-")
    try:
        cipher = work / "library.tar.gz.enc"
        print("[vault] 校验分块 …")
        assemble_cipher(vault, m, cipher)
        enc_key, mac_key = derive_keys(key, bytes.fromhex(m["kdf"]["salt"]), m["kdf"])
        if not hmac.compare_digest(hmac_sha256(mac_key, cipher), m["mac"]):
            die("HMAC 不符：密钥不对，或密文被篡改")
        plain = work / "library.tar.gz"
        print("[vault] 解密 …")
        openssl_crypt(openssl, enc_key, bytes.fromhex(m["kdf"]["iv"]), cipher, plain, decrypt=True)
        if file_sha256(plain) != m["plain"]["sha256"]:
            die("解密结果 sha256 不符")
        target.mkdir(parents=True, exist_ok=True)
        print("[vault] 解包到 " + str(target) + " …")
        with tarfile.open(plain, "r:gz") as tar:
            tar.extractall(target, filter="data")
        print("[vault] 完成：%d 个文件，%s" % (m["stats"]["files"], human(m["plain"]["bytes"])))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_info(args):
    vault = Path(args.vault)
    m = load_manifest(vault)
    total = sum(p["bytes"] for p in m["parts"])
    print("格式      " + m["format"])
    print("生成      " + str(m.get("created")))
    print("算法      %s  scrypt n=%d r=%d p=%d" % (m["cipher"], m["kdf"]["n"], m["kdf"]["r"], m["kdf"]["p"]))
    print("文件      %d 个，明文 tar.gz %s" % (m["stats"]["files"], human(m["plain"]["bytes"])))
    print("分块      %d 块，密文 %s" % (len(m["parts"]), human(total)))
    for p in m["parts"]:
        print("  %s  %s" % (p["name"], human(p["bytes"])))
    return 0


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="文库加密备份")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--library", default=str(DEFAULT_LIBRARY))
        p.add_argument("--vault", default=str(DEFAULT_VAULT))
        p.add_argument("--key-file", default=None)

    p = sub.add_parser("pack", help="打包 → 加密 → 切块写入 .library-vault/")
    common(p)
    p.add_argument("--part-size", type=int, default=PART_SIZE)
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("unpack", help="校验 → 解密 → 解包")
    common(p)
    p.add_argument("--target", default=str(DEFAULT_LIBRARY))
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_unpack)

    p = sub.add_parser("verify", help="只校验（有密钥时校验 HMAC）")
    common(p)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("info", help="查看 manifest 概要")
    common(p)
    p.set_defaults(func=cmd_info)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
