import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        return struct.pack(
            "!10I20sH"
            + str(len(self.name))
            + "s"
            + str(8 - (62 + len(self.name)) % 8)
            + "x",
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino & 0xFFFFFFFF,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            self.name.encode(),
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        data_list = list(struct.unpack("!10I20sH" + str(len(data) - 62) + "s", data))
        data_list[-1] = data_list[-1].strip(b"\00").decode()
        return GitIndexEntry(*data_list)


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    result = []  # type: ignore
    if (gitdir / "index").exists() == False:
        return result
    data = (gitdir / "index").open("rb").read()
    start_pos = 12
    for i in range(struct.unpack("!I", data[8:start_pos])[0]):
        end_pos = data.index(b"\00", start_pos + 62)
        while (end_pos - 11) % 8 > 0:
            end_pos += 1
        result.append(GitIndexEntry.unpack(data[start_pos : end_pos + 1]))
        start_pos = end_pos + 1
    return result


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    data = b"DIRC" + struct.pack("!2I", 2, len(entries))
    for entry in entries:
        data += entry.pack()
    with (gitdir / "index").open("wb") as f:
        f.write(data)
        f.write(hashlib.sha1(data).digest())


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    for entry in read_index(gitdir):
        print(
            f"{entry.mode:o}" + " " + entry.sha1.hex() + " 0\t" + entry.name
        ) if details else print(entry.name)


def update_index(
    gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True
) -> None:
    entries = read_index(gitdir)
    for path in paths:
        s = path.stat()
        entries.append(
            GitIndexEntry(
                ctime_s=int(s.st_ctime),
                ctime_n=0,
                mtime_s=int(s.st_mtime),
                mtime_n=0,
                dev=s.st_dev,
                ino=s.st_ino,
                mode=s.st_mode,
                uid=s.st_uid,
                gid=s.st_gid,
                size=s.st_size,
                sha1=bytes.fromhex(
                    hash_object(path.open("rb").read(), "blob", write=True)
                ),
                flags=len(path.name),
                name=str(path),
            )
        )
    write_index(gitdir, sorted(entries, key=lambda entry: entry.name)) if write else ""
