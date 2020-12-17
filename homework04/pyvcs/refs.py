import pathlib
import typing as tp


def update_ref(
    gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str
) -> None:
    with (gitdir / ref).open("w") as file:
        file.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    with (gitdir / name).open("w") as file:
        file.write("ref: " + ref)


def ref_resolve(gitdir: pathlib.Path, refname: str) -> tp.Optional[str]:
    if refname == "HEAD" and not is_detached(gitdir):
        return str(resolve_head(gitdir))
    return (
        str((gitdir / refname).open().read().strip())
        if (gitdir / refname).exists()
        else None
    )


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    return ref_resolve(gitdir, get_ref(gitdir))


def is_detached(gitdir: pathlib.Path) -> bool:
    return True if get_ref(gitdir) == "" else False


def get_ref(gitdir: pathlib.Path) -> str:
    data = (gitdir / "HEAD").open().read().strip().split()
    return data[1] if len(data) == 2 else ""
