


try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    # pyrefly: ignore [missing-import]
    from kivy.properties import StringProperty, ListProperty, BooleanProperty
    from kivy.lang import Builder
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.dropdown import DropDown
    from kivy.metrics import dp
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.factory import Factory
except ModuleNotFoundError:
    raise SystemExit("Install kivy using: pip install kivy")

from kivy.config import Config
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '550')

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


# ----------------------------------------------------
# JOURNAL PROMPTS (Feature 2)
# ----------------------------------------------------
JOURNAL_PROMPTS = [
    "What's today's vibe? ✨",
    "How was your day?",
    "What made you smile today?",
    "What are you grateful for today?",
    "What's on your mind?",
    "What's one thing you want to remember about today?",
    "How did today make you feel?"
]

def get_prompt_for_date(date_str):
    """Deterministic selection of a journaling prompt based on date."""
    idx = sum(ord(c) for c in str(date_str)) % len(JOURNAL_PROMPTS)
    return JOURNAL_PROMPTS[idx]


# ----------------------------------------------------
# CUSTOM WIDGET CLASSES
# ----------------------------------------------------
class CompactDropDown(DropDown):
    """Compact scrollable dropdown that will not cover the screen."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_height = dp(220)


class TaskCard(BoxLayout):
    """Modern card container for each to-do item."""
    completed = BooleanProperty(False)


# Register widgets with Factory so KV can instantiate them
Factory.register('CompactDropDown', cls=CompactDropDown)
Factory.register('TaskCard', cls=TaskCard)


# Load KV layout
Builder.load_file(resource_path("ediary.kv"))


# ----------------------------------------------------
# HOME / CALENDAR SCREEN (Feature 1)
# ----------------------------------------------------
class HomeScreen(Screen):

    months = ListProperty(calendar.month_name[1:])

    def on_enter(self):
        self.today = datetime.now()
        if not hasattr(self, 'year') or not self.year:
            self.year = self.today.year
            self.month = self.today.month

        self._sync_selectors_and_render()

    def get_year_range(self):
        """Generate a reasonable year range around current/selected year."""
        curr_year = datetime.now().year
        start_y = min(curr_year - 15, self.year - 2)
        end_y = max(curr_year + 15, self.year + 2)
        return [str(y) for y in range(start_y, end_y + 1)]

    def _sync_selectors_and_render(self):
        self.ids.year_spinner.values = self.get_year_range()
        self.ids.year_spinner.text = str(self.year)
        self.ids.month_spinner.text = calendar.month_name[self.month]
        self.render_calendar()

    def on_year_selected(self, text):
        try:
            val = int(text)
            if val != self.year:
                self.year = val
                self.ids.year_spinner.values = self.get_year_range()
                self.render_calendar()
        except (ValueError, TypeError):
            pass

    def on_month_selected(self, text):
        if text in calendar.month_name:
            val = list(calendar.month_name).index(text)
            if val != self.month and val > 0:
                self.month = val
                self.render_calendar()

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self._sync_selectors_and_render()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self._sync_selectors_and_render()

    def prev_year(self):
        self.year -= 1
        self._sync_selectors_and_render()

    def next_year(self):
        self.year += 1
        self._sync_selectors_and_render()

    def go_today(self):
        today = datetime.now()
        self.year = today.year
        self.month = today.month
        self._sync_selectors_and_render()

    def update_calendar(self):
        """Maintains backwards-compatibility with existing calls."""
        try:
            self.year = int(self.ids.year_spinner.text)
            self.month = list(calendar.month_name).index(self.ids.month_spinner.text)
        except Exception:
            pass
        self.render_calendar()

    def render_calendar(self):
        grid = self.ids.calendar_grid
        grid.clear_widgets()

        today = datetime.now()
        is_current_month = (self.year == today.year and self.month == today.month)

        # Days header
        day_headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, d in enumerate(day_headers):
            is_weekend = (i >= 5)
            color = (0.75, 0.60, 0.70, 1) if is_weekend else (0.55, 0.62, 0.75, 1)
            grid.add_widget(Label(text=d, bold=True, color=color, font_size='13sp'))

        # Calendar days
        for week in calendar.monthcalendar(self.year, self.month):
            for day in week:
                if day == 0:
                    grid.add_widget(Label(text=""))
                else:
                    is_today = (is_current_month and day == today.day)
                    
                    if is_today:
                        bg_color = (0.28, 0.45, 0.90, 1)
                        txt_color = (1, 1, 1, 1)
                        is_bold = True
                    else:
                        bg_color = (0.16, 0.19, 0.26, 1)
                        txt_color = (0.90, 0.92, 0.96, 1)
                        is_bold = False

                    btn = Button(
                        text=str(day),
                        background_normal="",
                        background_color=bg_color,
                        color=txt_color,
                        bold=is_bold,
                        font_size='14sp'
                    )
                    btn.bind(on_press=lambda x, d=day: self.open_entry(d))
                    grid.add_widget(btn)

        self.ids.month_title.text = f"{calendar.month_name[self.month]} {self.year}"

    def open_entry(self, day):
        date = f"{self.year}-{self.month:02}-{day:02}"
        screen = self.manager.get_screen("diary")
        screen.load_entry(date)
        self.manager.current = "diary"


# ----------------------------------------------------
# DIARY & TO-DO SCREEN (Features 2 & 3)
# ----------------------------------------------------
class DiaryScreen(Screen):

    current_date = StringProperty("")

    def load_entry(self, date):
        self.current_date = date

        content = database.get_entry(date)

        # Feature 2: Empty-state prompts
        prompt = get_prompt_for_date(date)
        self.ids.editor.hint_text = prompt
        self.ids.editor.text = content if content else ""
        self.ids.diary_title.text = f"Diary — {date}"
        
        if hasattr(self.ids, 'save_feedback'):
            self.ids.save_feedback.text = ""

        self.load_tasks()

    def save(self):
        text_to_save = self.ids.editor.text
        # Ensure empty text or prompt is never saved into SQLite
        if text_to_save in JOURNAL_PROMPTS:
            text_to_save = ""
        database.save_entry(self.current_date, text_to_save)

        # Visual feedback for saving
        if hasattr(self.ids, 'save_feedback'):
            self.ids.save_feedback.text = "Saved ✔"
            Clock.schedule_once(lambda dt: setattr(self.ids.save_feedback, 'text', ''), 2.0)

    def go_home(self):
        self.manager.current = "home"

    # ---------- TO-DO SYSTEM (Feature 3) ----------
    def load_tasks(self):
        container = self.ids.tasks_container
        container.clear_widgets()

        tasks = database.get_tasks_by_date(self.current_date)

        if not tasks:
            # Empty state message
            empty_card = Factory.EmptyTaskCard()
            container.add_widget(empty_card)
            return

        priority_colors = {
            "High": (0.95, 0.35, 0.35, 1),
            "Medium": (0.96, 0.65, 0.22, 1),
            "Low": (0.28, 0.80, 0.50, 1)
        }

        for tid, task, priority, done in tasks:
            is_done = bool(done)
            card = TaskCard(completed=is_done)

            # Priority badge / dot
            p_color = priority_colors.get(priority, (0.7, 0.7, 0.7, 1))
            badge = Label(
                text=f"● {priority}",
                size_hint_x=None,
                width=72,
                color=p_color,
                font_size='11sp',
                bold=True
            )

            # Task title
            task_display = ("✔ " if is_done else "") + task
            text_color = (0.50, 0.54, 0.62, 1) if is_done else (0.94, 0.96, 0.98, 1)
            label = Label(
                text=task_display,
                color=text_color,
                halign="left",
                valign="middle",
                font_size='13sp',
                shorten=True,
                shorten_from='right'
            )
            label.bind(size=label.setter('text_size'))

            # Done button
            if is_done:
                done_btn = Button(
                    text="✔",
                    size_hint_x=None,
                    width=40,
                    background_normal="",
                    background_color=(0.14, 0.26, 0.18, 0.7),
                    color=(0.4, 0.75, 0.5, 1),
                    font_size='14sp',
                    bold=True
                )
            else:
                done_btn = Button(
                    text="✓",
                    size_hint_x=None,
                    width=40,
                    background_normal="",
                    background_color=(0.18, 0.55, 0.32, 1),
                    color=(1, 1, 1, 1),
                    font_size='15sp',
                    bold=True
                )
            done_btn.bind(on_press=lambda x, t=tid: self.complete_task(t))

            # Delete button
            del_btn = Button(
                text="✕",
                size_hint_x=None,
                width=36,
                background_normal="",
                background_color=(0.28, 0.16, 0.18, 0.7),
                color=(0.95, 0.45, 0.45, 1),
                font_size='13sp',
                bold=True
            )
            del_btn.bind(on_press=lambda x, t=tid: self.delete_task(t))

            card.add_widget(badge)
            card.add_widget(label)
            card.add_widget(done_btn)
            card.add_widget(del_btn)

            container.add_widget(card)

    def add_task(self):
        task = self.ids.task_input.text.strip()
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


# ----------------------------------------------------
# APPLICATION
# ----------------------------------------------------
class MiniDiaryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DiaryScreen(name="diary"))
        return sm


if __name__ == "__main__":
    MiniDiaryApp().run()
