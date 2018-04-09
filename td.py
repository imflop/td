import os
import sys
import json
import click
import base64
from typing import Union
from platform import system
from datetime import datetime


TD_LIST_FILE_NAME = "td.json"


class Storage(object):
    """ Get dropbox location if exist in a system """
    def __init__(self):
        self.current_system = system()
        if self.current_system in ('Windows', 'cli'):
            self.host_db_path = os.path.join(
                self._get_appdata_path(), 'Dropbox', 'host.db'
            )
            self.dropbox_location = self._read_from_path(self.host_db_path)
        elif self.current_system in ('Linux', 'Darwin'):
            self.host_db_path = os.path.expanduser('~''/.dropbox''/host.db')
            self.dropbox_location = self._read_from_path(self.host_db_path)
            if self._is_td_folder_exists(self.dropbox_location + "/.td/"):
                self.path_to_file = self.dropbox_location + '/.td/'
            else:
                self.path_to_file = self._create_td_folder(
                    self.dropbox_location + '/.td/')
        else:
            raise RuntimeError('Unknown system={}'.format(self.current_system))

        if not os.path.exists(self.host_db_path):
            # TODO: create folder into the user home directory
            raise RuntimeError(
                'Dropbox does not exists'.format(self.current_system)
            )

    def _is_td_folder_exists(self, path: str) -> bool:
        return os.path.isdir(path)

    def _create_td_folder(self, path: str) -> str:
        try:
            os.makedirs(path)
            return path
        except OSError as e:
            raise e

    def _get_appdata_path(self) -> str:
        return ""

    def _read_from_path(self, path: str) -> str:
        with open(path, 'r') as f:
            self.data = f.read().split()
            return base64.b64decode(self.data[1]).decode('utf-8')

    def get_path_to_file(self) -> str:
        return self.path_to_file + TD_LIST_FILE_NAME


class TaskDict(object):
    """ Task list, finished and unfinished """
    def __init__(self):
        """ Init task list dict from file """
        self.td_home_location = Storage().get_path_to_file()
        try:
            with open(self.td_home_location, "r") as json_file:
                self.td_task_list = json.load(json_file)
        except IOError as e:
            if e.errno == 2:  # no such file, create file
                with open(self.td_home_location, "w") as json_file:
                    json_file.write("{}")
                with open(self.td_home_location, "r") as json_file:
                    self.td_task_list = json.load(json_file)

    def _write_data(self, td_data: dict):
        """ Flush data to disk """
        with open(self.td_home_location, "w") as td_json_file:
            td_json_file.write(json.dumps(td_data, indent=4))

    def _show_icon_by_task_status(self, status: bool) -> str:
        return "☐" if status is False else "✔"

    def _show_nice_completed_date(self, completed_date: str) -> str:
        if completed_date != "":
            return "@done at {d}".format(d=datetime.strptime(
                completed_date, '%d-%m-%Y %H:%M:%S').strftime('%d-%m-%Y %H:%M'))
        else:
            return ""

    def add_task(self, text: str):
        """ Adding new task to dict """
        new_task = dict(
            text=text,
            is_done=False,
            created_at=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            completed_at=""
        )
        if not self.td_task_list:
            new_id = 1
        else:
            last_id = sorted(self.td_task_list.keys())[-1]
            new_id = int(last_id) + 1
        self.td_task_list.update({new_id: new_task})
        self._write_data(self.td_task_list)

    def remove_task_by_id(self, task_id: int):
        """ Remove task from dict by task id """
        # TODO: if list is empty show message about it
        if self.td_task_list.get(str(task_id)):
            del self.td_task_list[str(task_id)]
            self._write_data(self.td_task_list)
            print("Task {id} successfully removed".format(id=task_id))
        else:
            print("Task {id} not found".format(id=task_id))

    def finish_task_by_id(self, task_id: int):
        """ Mark task as completed by task id """
        # TODO: if list is empty show message about it
        current_task = self.td_task_list.pop(str(task_id), None)
        current_task.update({
            "is_done": True,
            "completed_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })
        self.td_task_list.update({task_id: current_task})
        self._write_data(self.td_task_list)
        print("Task {id} successfully finished".format(id=task_id))

    def print_task_list(self, task_status: Union[bool, None]):
        if task_status is not None:
            for key, value in sorted(
                    self.td_task_list.items(),
                    key=lambda x: x[1]["created_at"],
                    reverse=True
            ):
                if value["is_done"] is task_status:
                    print("{id}: {icon} {text} {date}".format(
                        id=key,
                        icon=self._show_icon_by_task_status(task_status),
                        text=value["text"],
                        date=self._show_nice_completed_date(value["completed_at"]))
                    )
        else:
            for key, value in sorted(
                    self.td_task_list.items(),
                    key=lambda x: x[1]["created_at"],
                    reverse=True
            ):
                if value["is_done"] is False:
                    print("{id}: {icon} {text}".format(
                        id=key,
                        icon=self._show_icon_by_task_status(False),
                        text=value["text"])
                    )

            for key, value in sorted(
                    self.td_task_list.items(),
                    key=lambda x: x[1]["created_at"],
                    reverse=True
            ):
                if value["is_done"] is True:
                    print("{id}: {icon} {text} {date}".format(
                        id=key,
                        icon=self._show_icon_by_task_status(True),
                        text=value["text"],
                        date=self._show_nice_completed_date(value["completed_at"]))
                    )


@click.command()
@click.option('-l', 'option', flag_value='all', help='Show all tasks in the list')
@click.option('-o', 'option', flag_value='open', help='Show only open tasks')
@click.option('-c', 'option', flag_value='close', help='Show closed tasks only')
@click.option('-a', '--add', help='Just type something to adding to task list')
@click.option('-r', '--remove', type=int, help='Remove task by id')
@click.option('-f', '--finish', type=int, help='Finish task by id')
def _main(option, remove, finish, add):
    td = TaskDict()
    if option is 'all':
        td.print_task_list(None)
    elif option is 'open':
        td.print_task_list(False)
    elif option is 'close':
        td.print_task_list(True)
    elif remove is not None:
        td.remove_task_by_id(int(remove))
    elif finish is not None:
        td.finish_task_by_id(int(finish))
    elif add is not None:
        td.add_task(add)
        td.print_task_list(False)


if __name__ == '__main__':
    prefixes = (
        '-a', '-r', '-f', '-l', '-o', '-c', '--add', '--remove', '--finish',
    )
    if len(sys.argv[1:]) != 0:
        input_text = " ".join(sys.argv[1:]).strip()
        if input_text.startswith(prefixes):
            _main()
        else:
            task_dict = TaskDict()
            task_dict.add_task(input_text)
            task_dict.print_task_list(False)
    else:
        click.echo(click.style(
            "Next time to adding task type something ...", fg="red")
        )
