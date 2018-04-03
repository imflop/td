import json
import click
from typing import Union
from datetime import datetime


class TaskDict(object):
    """ Task list, finished and unfinished """
    def __init__(self):
        """ Init task list dict from file """
        try:
            with open("td.json", "r") as json_file:
                self.td_task_list = json.load(json_file)
        except IOError as e:
            if e.errno == 2:  # no such file, create file
                with open("td.json", "w") as json_file:
                    json_file.write("[{}]")

    @staticmethod
    def _write_data(td_data: dict):
        """ Flush data to disk """
        with open("td.json", "w") as td_json_file:
            td_json_file.write(json.dumps(td_data, indent=4))

    @staticmethod
    def _show_icon_by_task_status(status: bool) -> str:
        return "☐" if status is False else "✔"

    @staticmethod
    def _show_nice_completed_date(completed_date: str) -> str:
        if completed_date != "":
            return "@done at {d}".format(d=datetime.strptime(
                completed_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'))
        else:
            return ""

    def add_task(self, text: str):
        """ Adding new task to dict """
        # TODO: if list is empty starts id form 1
        new_task = dict(
            text=text,
            is_done=False,
            created_at=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            completed_at=""
        )
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
@click.option('-l', 'option', flag_value='all', help='Show all tasks in list')
@click.option('-o', 'option', flag_value='open', help='Show only open tasks')
@click.option('-c', 'option', flag_value='close', help='Show only close tasks')
@click.option('-a', '--add', help='Just type something to adding to task list')
@click.option('-r', '--remove', help='Remove task by id')
@click.option('-f', '--finish', help='Finish task by id')
def _main(option, remove, finish, add):
    td = TaskDict()
    if option is 'all':
        td.print_task_list(task_status=None)
    elif option is 'open':
        td.print_task_list(task_status=False)
    elif option is 'close':
        td.print_task_list(task_status=True)
    elif remove is not None:
        td.remove_task_by_id(int(remove))
    elif finish is not None:
        td.finish_task_by_id(int(finish))
    elif add is not None:
        td.add_task(add)
        td.print_task_list(task_status=False)


if __name__ == '__main__':
    import sys
    prefixes = (
        '-a', '-r', '-f', '-l', '-o', '-c', '--add', '--remove', '--finish',
    )
    if len(sys.argv[1:]) != 0:
        text = " ".join(sys.argv[1:]).strip()
        if text.startswith(prefixes):
            _main()
        else:
            task_dict = TaskDict()
            task_dict.add_task(text)
            task_dict.print_task_list(task_status=False)
    else:
        click.echo(click.style(
            "Next time to adding task type something ...", fg="red")
        )
