import dataclasses as dc
import hashlib
import typing as t
from collections import abc

from enum import IntEnum
from pathlib import Path


class InvalidTDFile(Exception):
    ...


class IOErrorNumber(IntEnum):
    NO_SUCH_FILE = 2


@dc.dataclass(slots=True)
class TD:
    td_dir: str = dc.field(default=".td")
    td_name: str = dc.field(default="td")
    tasks: abc.MutableMapping[str, t.Any] = dc.field(init=False)

    def __post_init__(self):
        td_path = self._get_path_to_file()

        if not Path(td_path).exists():
            td_path = self._create_folder_and_file(td_path)

        self.tasks = self._read_tasks(td_path)

    def add(self, text: str) -> None:
        task_id = hashlib.sha1(text.encode("utf-8")).hexdigest()
        self.tasks[task_id] = {"id": task_id, "text": text}

    def edit(self) -> None:
        ...

    def finish(self) -> None:
        ...

    def print_list(self) -> None:
        for tid, value in self.tasks.items():
            print(f"TID: {tid}")
            print(f"VALUE: {value}")

    def write(self, td_data: t.Any) -> None:
        with open(self._get_path_to_file(), "w") as f:
            f.write(td_data)

    def _get_path_to_file(self) -> Path:
        return Path.home().joinpath(f"{self.td_dir}/{self.td_name}")

    @staticmethod
    def _read_tasks(path_to_file: Path) -> dict:
        try:
            with open(path_to_file, "r") as td_file:
                raw_data = [task_line.strip() for task_line in td_file if task_line]
                if not raw_data:
                    return {}
        except IOError as e:
            if e.errno == IOErrorNumber.NO_SUCH_FILE:
                with open(path_to_file, "r+") as td_file:
                    td_file.write("")
                    td_file.flush()
                    td_file.seek(0)
                    return td_file.read()

    @staticmethod
    def _create_folder_and_file(path_to_create: Path) -> Path:
        path = Path(path_to_create)
        path.parent.mkdir()
        path.write_text("")

        return path


def main():
    td = TD()

    for i in range(5):
        td.add(f"text {i}")

    td.print_list()


if __name__ == "__main__":
    main()
