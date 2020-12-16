import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    fmt_data = (fmt + " " + str(len(data))).encode() + b"\00" + data
    hash_sum = hashlib.sha1(fmt_data).hexdigest()
    if write:
        path = repo_find() / "objects" / hash_sum[:2]
        pathlib.Path(path).mkdir(exist_ok=True)
        with (path / hash_sum[2:]).open("wb") as f:
            f.write(zlib.compress(fmt_data))
    return hash_sum


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    if (4 <= len(obj_name) <= 40) == False:
        raise Exception("Not a valid object name %s" % (obj_name))
    result = []
    for file in (gitdir / "objects" / obj_name[:2]).glob(obj_name[2:] + "*"):
        result.append(obj_name[:2] + file.name)
    if len(result) == 0:
        raise Exception("Not a valid object name %s" % (obj_name))
    return result


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # There are no tests fot this function, therefore...
    return str(gitdir) + "/" + obj_name[:2] + "/" + obj_name[2:]


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    data = zlib.decompress((gitdir / "objects" / sha[:2] / sha[2:]).open("rb").read())
    return data.split(b" ")[0].decode(), data.split(b"\00", maxsplit=1)[1]


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    result = []
    while data:
        sha = data.index(b"\00")
        mode, name = map(lambda x: x.decode(), data[:sha].split(b" "))
        result.append((int(mode), data[sha + 1 : sha + 21].hex(), name))
        data = data[sha + 21 :]
    return result


def cat_file(obj_name: str, pretty: bool = True) -> None:
    type, data = read_object(obj_name, repo_find())
    if type in ("blob", "commit"):
        print(data.decode())
        return
    for i in read_tree(data):
        print(f"{i[0]:06}", "tree" if i[0] == 40000 else "blob", i[1] + "\t" + i[2])


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    # There are no tests fot this function, therefore...
    result = []
    header, data = read_object(tree_sha, gitdir)
    for file in read_tree(data):
        if read_object(file[2], gitdir)[0] == "tree":
            tree = find_tree_files(file[2], gitdir)
            result = [(file[1] + "/" + blob[0], blob[1]) for blob in tree]
        else:
            result.append((file[1], file[2]))
    return result


def commit_parse(raw: bytes, start: int = 0, dct=None):
    data = {"message": []}  # type: ignore
    for line in raw.decode().split("\n"):
        if line.startswith(("tree", "parent", "author", "committer")):
            name, value = line.split(" ", maxsplit=1)
            data[str(name)] = value  # type: ignore
        else:
            data["message"].append(line)
    return data
