import argparse
import os
import zipfile

from bs4 import BeautifulSoup
from requests.sessions import Session
from zipfile import ZipFile

TARGET_DIR = ".build"
TARGET_FILENAME = "Apora-Dict2Anki.zip"


def create_zip(
    target_dir=TARGET_DIR, target_filename=TARGET_FILENAME, share_outside=False
):
    file_paths = []
    exclude_dirs = [
        "build",
        "_image",
        "test",
        "test_addon",
        "testapi",
        "__pycache__",
        ".git",
        ".idea",
        ".pytest_cache",
        "screenshots",
        "venv",
        ".venv",
        ".ruff_cache",
        ".vscode",
    ]
    exclude_files = [
        "README.md",
        "SUPPORT.md",
        "Makefile",
        "Makefile.bat",
        "apitest.py",
        "constants_tests.py",
        "words.txt",
        "NOTE.txt",
        "test.py",
        "testqt.py",
        "apitest_eudict.py",
        "apitest_youdao.py",
        "FixQtEnums.py",
        ".gitignore",
        ".travis.yml",
        "deploy.py",
        "requirements.txt",
        ".DS_Store",
        "meta.json",
        "manifest.json",
    ]

    if share_outside:
        exclude_files.remove("manifest.json")

    exclude_ext = {".png", ".ui", ".qrc", ".log", ".zip", ".tpl", ".sh"}
    for dirname, sub_dirs, files in os.walk("."):
        # 跳过排除的目录
        sub_dirs[:] = [d for d in sub_dirs if d not in exclude_dirs]

        # 判断当前是否在 assets 目录下（支持 assets/subfolder）
        in_assets = (
            dirname.startswith(os.path.join(".", "assets"))
            or dirname.find("assets") > -1
        )

        for f in files[:]:
            # 排除指定文件名
            if f in exclude_files:
                continue

            # 如果不在 assets 目录下，才应用扩展名过滤
            if not in_assets:
                if os.path.splitext(f)[1].lower() in exclude_ext:
                    continue

            file_paths.append(os.path.join(dirname, f))

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    filepath = os.path.join(target_dir, target_filename)
    with ZipFile(filepath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in file_paths:
            zf.write(file)
    print(f"File [{filepath}] saved.")


def publish(zip_dir, zip_filename, title, tags, desc):
    """TODO"""
    username = os.environ.get("ANKI_USERNAME")
    password = os.environ.get("ANKI_PASSWORD")
    addon_id = os.environ.get("ANKI_ADDON_ID")

    if not username:
        username = input("Anki username: ")
    if not addon_id:
        addon_id = input("Anki addon ID: ")

    print("username:", username)
    print("addon_id:", addon_id)

    if not password:
        password = input("Anki password: ")

    s = Session()
    URL = "https://ankiweb.net/account/login"
    rsp = s.get(URL)
    soup = BeautifulSoup(rsp.text, features="html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})

    if csrf_token is None:
        raise Exception("Cannot get csrf_token")

    csrf_token_value = csrf_token.get("value")
    s.post(
        URL,
        data={
            "submit": 1,
            "csrf_token": csrf_token_value,
            "username": username,
            "password": password,
        },
    )

    URL = "https://ankiweb.net/shared/upload"
    filepath = os.path.join(zip_dir, zip_filename)
    file = {"v21file": open(filepath, "rb")}
    rsp = s.post(
        URL,
        files=file,
        data={
            "title": title,
            "tags": tags,
            "desc": desc,
            "id": addon_id,
            "submit": "Update",
            "v21file": file,
            "v20file": "",
        },
    )
    s.close()
    if rsp.url == f"https://ankiweb.net/shared/info/{addon_id}":
        return True
    else:
        return False


if __name__ == "__main__":
    OPERATIONS = ["build", "build-x", "publish"]
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", type=str, choices=OPERATIONS, help="cluster name")
    parser.add_argument("-d", "--dir", type=str, help="target directory")
    args = parser.parse_args()

    operation: str = args.operation
    directory = args.dir
    if not directory:
        directory = TARGET_DIR

    # print(operation, directory)
    print(f"operation: {operation}")
    print(f"directory: {directory}")

    match operation:
        case "build":
            create_zip(target_dir=directory)
        case "build-x":
            create_zip(target_dir=directory, share_outside=True)
        case "publish":
            raise RuntimeError(f"Operation '{operation}' is not implemented yet")
        case _:
            raise RuntimeError(f"Unsupported operation: {operation}")
