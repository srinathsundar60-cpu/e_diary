try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.properties import StringProperty, ListProperty
    from kivy.lang import Builder
except ModuleNotFoundError:
    raise SystemExit("Install kivy using: pip install kivy")

import os
import sys
import calendar
from datetime import datetime
import database


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS   
    except Exception:
        base_path = os.path.abspath(".")  
    return os.path.join(base_path, relative_path)


Builder.load_file(resource_path("ediary.kv"))


class HomeScreen(Screen):

    months = ListProperty(calendar.month_name[1:])

    def on_enter(self):
        self.year = datetime.now().year
        self.month = datetime.now().month

        self.ids.year_spinner.text = str(self.year)
        self.ids.month_spinner.text = calendar.month_name[self.month]

        self.render_calendar()

    def update_calendar(self):
        self.year = int(self.ids.year_spinner.text)
        self.month = list(calendar.month_name).index(
            self.ids.month_spinner.text
        )
        self.render_calendar()

    def render_calendar(self):
        grid = self.ids.calendar_grid
        grid.clear_widgets()

        from kivy.uix.button import Button
        from kivy.uix.label import Label

        # Days header
        for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            grid.add_widget(Label(text=d, bold=True))

        # Calendar days
        for week in calendar.monthcalendar(self.year, self.month):
            for day in week:
                if day == 0:
                    grid.add_widget(Label(text=""))
                else:
                    btn = Button(
                        text=str(day),
                        background_normal="",
                        background_color=(0.18, 0.22, 0.30, 1)
                    )
                    btn.bind(on_press=lambda x, d=day: self.open_entry(d))
                    grid.add_widget(btn)

        self.ids.month_title.text = f"{calendar.month_name[self.month]} {self.year}"

    def open_entry(self, day):
        date = f"{self.year}-{self.month:02}-{day:02}"
        screen = self.manager.get_screen("diary")
        screen.load_entry(date)
        self.manager.current = "diary"

class DiaryScreen(Screen):

    current_date = StringProperty("")

    def load_entry(self, date):
        self.current_date = date

        content = database.get_entry(date)

        self.ids.editor.text = content
        self.ids.diary_title.text = f"Diary — {date}"

        self.load_tasks()

    def save(self):
        database.save_entry(self.current_date, self.ids.editor.text)

    def go_home(self):
        self.manager.current = "home"


    # ---------- TODO ----------
    def load_tasks(self):
        container = self.ids.tasks_container
        container.clear_widgets()

        tasks = database.get_tasks_by_date(self.current_date)

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        priority_colors = {
            "High": (1, 0.3, 0.3, 1),
            "Medium": (1, 0.7, 0.2, 1),
            "Low": (0.3, 0.9, 0.4, 1)
        }

        for tid, task, priority, done in tasks:

            row = BoxLayout(
                size_hint_y=None,
                height=45,
                spacing=8,
                padding=5
            )

            badge = Label(
                text=priority,
                size_hint_x=None,
                width=80,
                color=priority_colors.get(priority, (1, 1, 1, 1)),
                bold=True
            )

            label = Label(
                text=("✔ " if done else "") + task,
                halign="left"
            )
            label.bind(size=label.setter('text_size'))

            done_btn = Button(
                text="Done",
                size_hint_x=None,
                width=70,
                background_normal="",
                background_color=(0.2, 0.6, 0.3, 1)
            )
            done_btn.bind(on_press=lambda x, t=tid: self.complete_task(t))

            del_btn = Button(
                text="X",
                size_hint_x=None,
                width=50,
                background_normal="",
                background_color=(0.7, 0.2, 0.2, 1)
            )
            del_btn.bind(on_press=lambda x, t=tid: self.delete_task(t))

            row.add_widget(badge)
            row.add_widget(label)
            row.add_widget(done_btn)
            row.add_widget(del_btn)

            container.add_widget(row)

    def add_task(self):
        task = self.ids.task_input.text
        priority = self.ids.priority_spinner.text

        if task:
            database.add_task_with_date(
                task,
                self.current_date,
                priority
            )

            self.ids.task_input.text = ""
            self.load_tasks()

    def complete_task(self, tid):
        database.complete_task(tid)
        self.load_tasks()

    def delete_task(self, tid):
        database.delete_task(tid)
        self.load_tasks()


class MiniDiaryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DiaryScreen(name="diary"))
        return sm


MiniDiaryApp().run()
