import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    name = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    while pathlib.Path(workdir.absolute().root) != workdir.absolute():
        if (workdir / name).is_dir():
            return workdir / name
        workdir = workdir.parent
    if (workdir / name).is_dir():
        return workdir / name
    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    if os.path.isfile(workdir):
        raise Exception("%s is not a directory" % (workdir))
    gitdir = (
        pathlib.Path(os.environ["GIT_DIR"])
        if os.getenv("GIT_DIR")
        else pathlib.Path(".pyvcs")
    )
    os.mkdir(gitdir)
    for folder in ["objects", "refs", "refs/heads", "refs/tags"]:
        os.makedirs(os.path.join(gitdir, folder), exist_ok=True)
    with open(gitdir / "HEAD", "w") as f:
        f.write("ref: refs/heads/master\n")
    with open(gitdir / "config", "w") as f:
        f.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
        )
    with open(gitdir / "description", "w") as f:
        f.write("Unnamed pyvcs repository.\n")
    return workdir / gitdir
