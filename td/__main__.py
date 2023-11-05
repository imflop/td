import dataclasses as dc
import hashlib
import typing as t
from collections import abc
from datetime import datetime

from enum import IntEnum
from pathlib import Path


class InvalidTDFile(Exception):
    def __int__(self, path: Path, error: str):
        super().__init__()
        self.path = path
        self.error = error


class TaskStatus(IntEnum):
    ACTIVE = 0
    FINISHED = 1


@dc.dataclass(slots=True, frozen=True, repr=False)
class TD:
    td_dir: str = dc.field(default=".td")
    td_name: str = dc.field(default="td")
    tasks: abc.MutableMapping[str, t.Any] = dc.field(init=False)

    def __post_init__(self):
        td_path = self._get_path_to_file()

        if not Path(td_path).exists():
            td_path = self._create_folder_and_file(td_path)

        object.__setattr__(self, "tasks", self._read_tasks(td_path))

    def __getitem__(self, prefix: str) -> str:
        prefixes_task_ids_map = self._get_prefixes({k for k in self.tasks.keys()})

        if not (task_id := prefixes_task_ids_map.get(prefix)):
            raise

        return task_id

    def add(self, text: str, status: TaskStatus = TaskStatus.ACTIVE) -> None:
        task_id = self._get_hash(text)
        created_ts = datetime.now().timestamp()
        self.tasks[task_id] = {"id": task_id, "text": text, "status": status, "cts": created_ts}

    def edit(self) -> None:
        ...

    def finish(self, prefix: str) -> None:
        self.tasks[self[prefix]]["status"] = TaskStatus.FINISHED

    def delete(self, prefix: str) -> None:
        self.tasks.pop(self[prefix])

    def print_list(self) -> None:
        tasks = self.tasks
        prefixes_map = self._get_prefixes({k for k in self.tasks.keys()})

        for prefix, task_id in prefixes_map.items():
            tasks[task_id]["prefix"] = prefix

        for key, value in tasks.items():
            icon = self._get_icon_by_status(int(value["status"]))
            print(f"{value['prefix']}: {icon} {value['text']}")

    def write(self) -> None:
        with open(self._get_path_to_file(), "w") as td_file:
            task_lines = self._get_task_lines_to_write(self.tasks)
            td_file.writelines(task_lines)

    def _get_path_to_file(self) -> Path:
        return Path.home().joinpath(self.td_dir, self.td_name)

    @staticmethod
    def _create_folder_and_file(path_to_create: Path) -> Path:
        path_to_create.parent.mkdir(parents=True, exist_ok=True)
        path_to_create.touch(exist_ok=True)

        return path_to_create

    def _read_tasks(self, path_to_file: Path) -> abc.Mapping[str, t.Any]:
        try:
            with open(path_to_file, "r") as td_file:
                if not (raw_data := [task_line.strip() for task_line in td_file if task_line]):
                    return {}

                tasks = map(self._get_tasks_from_raw_line, raw_data)

                return {task["id"]: task for task in tasks}
        except IOError as e:
            raise InvalidTDFile(path_to_file, e.strerror)

    @staticmethod
    def _get_tasks_from_raw_line(task_as_line: str) -> abc.Mapping[str, t.Any]:
        text, _, metadata = task_as_line.rpartition("|")
        task = {"text": text.strip()}

        for item in metadata.strip().split(";"):
            label, value = item.split(":")
            task[label.strip()] = value.strip()

        return task

    @staticmethod
    def _get_hash(text) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _get_prefixes(existed_tasks_ids: abc.Set[str]) -> abc.Mapping[str, str]:
        prefix_task_id_map = {}

        for tid in existed_tasks_ids:
            step = 2
            for i in range(0, len(tid), step):
                prefix = tid[i:i+step]

                if prefix in prefix_task_id_map:
                    # TODO: handle collision
                    break
                else:
                    prefix_task_id_map[prefix] = tid
                    break

        return prefix_task_id_map

    @staticmethod
    def _get_task_lines_to_write(tasks: abc.Mapping[str, t.Any]) -> abc.Sequence[str]:
        return [
            f"{value['text']} | id:{key}; status:{value['status']}; ts:{value['cts']};\n"
            for key, value in tasks.items()
        ]

    @staticmethod
    def _get_icon_by_status(task_status: int = 0) -> str:
        return "✔" if bool(task_status) else "☐"
