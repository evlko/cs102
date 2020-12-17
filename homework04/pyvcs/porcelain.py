import os
import pathlib
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import (
    commit_parse,
    find_object,
    find_tree_files,
    read_object,
    read_tree,
)
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    for path in paths:
        add(gitdir, list(path.glob("*"))) if path.is_dir() else update_index(
            gitdir, [path], True
        )


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    return commit_tree(
        gitdir,
        write_tree(gitdir, read_index(gitdir), str(gitdir.parent)),
        message,
        resolve_head(gitdir),
        author,
    )


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    for entry in read_index(gitdir):
        if pathlib.Path(entry.name).exists():
            os.remove(entry.name)
    commit_data = commit_parse(read_object(obj_name, gitdir)[1])
    complete = False
    while not complete:
        trees = [
            (gitdir.parent, read_tree(read_object(commit_data["tree"], gitdir)[1]))
        ]  # type: ignore
        while trees:
            tree_path, tree_content = trees.pop()
            for file_data in tree_content:
                fmt, data = read_object(file_data[1], gitdir)
                path = tree_path / file_data[2]
                if fmt == "tree":
                    trees.append((path, read_tree(data)))
                    if (path).exists() == False:
                        (path).mkdir()
                elif (path).exists() == False:
                    open(path, "wb").write(data)
        if "parent" in commit_data:
            commit_data = commit_parse((read_object(commit_data["parent"], gitdir)[1]))
        else:
            complete = True
    for dir in gitdir.parent.glob("*"):
        if dir != gitdir and dir.is_dir():
            try:
                os.removedirs(dir)
            except OSError:
                continue
