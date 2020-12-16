import os
import pathlib
import stat
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(
    gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = ""
) -> str:
    tree = []  # type: ignore
    subtrees = dict()  # type: ignore
    files = [str(file) for file in (gitdir.parent / dirname).glob("*")]
    for entry in index:
        if entry.name in files:
            tree.append((entry.mode, (gitdir.parent / entry.name), entry.sha1))
        else:
            subtree_dir = entry.name.lstrip(dirname).split("/", 1)[0]
            subtrees[subtree_dir] = []
            subtrees[subtree_dir].append(
                entry
            ) if subtree_dir in subtrees else subtrees[subtree_dir].append()

    for name in subtrees:
        tree.append(
            (
                0o40000,
                gitdir.parent / dirname / name,
                bytes.fromhex(
                    write_tree(
                        gitdir,
                        subtrees[name],
                        dirname + "/" + name if len(dirname) != 0 else name,
                    )
                ),
            )
        )
    tree.sort(key=lambda subtree: subtree[1])
    return hash_object(
        b"".join(
            (f"{e[0]:o}" + " " + e[1].name).encode() + b"\00" + e[2] for e in tree
        ),
        "tree",
        write=True,
    )


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    if (
        author is None
        and "GIT_AUTHOR_NAME" in os.environ
        and "GIT_AUTHOR_EMAIL" in os.environ
    ):
        author = str(
            str(os.getenv("GIT_AUTHOR_NAME", None))
            + " "
            + f'<{os.getenv("GIT_AUTHOR_EMAIL", None)}>'
        )  # type:ignore
    time_now = int(time.mktime(time.localtime()))
    time_zone = time.timezone
    time_text = "-" if time_zone > 0 else "+"
    time_zone = abs(time_zone)
    time_text += f"{time_zone // 60 // 60:02}{time_zone // 60 % 60:02}"
    text = ["tree %s" % (tree)]
    if parent is not None:
        text.append("parent %s" % (parent))
    sign = str(author) + " " + str(time_now) + " " + str(time_text)
    text.append("author %s" % (sign))
    text.append("committer %s" % (sign))
    text.append("\n" + message + "\n")
    return hash_object("\n".join(text).encode(), "commit", write=True)
