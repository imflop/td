import dataclasses as dc
import typing as t
import os

from enum import Enum
from pathlib import Path


class InvalidTDFile(Exception):
    ...


class IOErrorNumber(int, Enum):
    NO_SUCH_FILE = 2


@dc.dataclass(slots=True)
class TD:
    td_dir: str = dc.field(default=".td")
    td_name: str = dc.field(default="td")
    tasks: str = dc.field(default="")

    def __post_init__(self):
        td_path = self._get_path_to_file()

        if not Path(td_path).exists():
            td_path = self._create_folder_and_file(td_path)

        self.tasks = self._read_tasks(td_path)

    def add(self, text: str) -> None:
        self.tasks += f"{text} \n"
        self.write(self.tasks)

    def edit(self) -> None:
        ...

    def finish(self) -> None:
        ...

    def print_list(self) -> None:
        ...

    def write(self, td_data: t.Any) -> None:
        with open(self._get_path_to_file(), "w") as f:
            f.write(td_data)

    def _get_path_to_file(self) -> Path:
        return Path.home().joinpath(f"{self.td_dir}/{self.td_name}")

    @staticmethod
    def _read_tasks(path_to_file: Path) -> str:
        try:
            with open(path_to_file, "r") as td_file:
                return td_file.read()
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


if __name__ == "__main__":
    main()
