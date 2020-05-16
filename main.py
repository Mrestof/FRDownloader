from kivy.app import App
from kivy.core.window import Window

from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.properties import ListProperty


# Screens
class FRDScreenManager(ScreenManager):
    pass


class FRDMain(Screen):
    pass


class FRDBrowse(Screen):

    def add_tile(self):
        grid_layout = self.ids['items']
        grid_layout.add_widget(FRDButton(
            text='i\'m the new tile',
            size_hint_y=None,
            height=240
        ))


# todo make an FRDMyCollectionManager screen


# Widgets
class FRDButton(Button):
    pass


class FRDSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.option_cls = FRDSpinnerOption


class FRDSpinnerOption(SpinnerOption):
    pass


class FRDApp(App):
    dark_blue = ListProperty([0.086, 0.141, 0.278, 1])
    light_blue = ListProperty([0.122, 0.251, 0.408, 1])
    dark_purple = ListProperty([0.106, 0.106, 0.184, 1])
    pink = ListProperty([0.894, 0.247, 0.353, 1])

    def build(self):
        Window.clearcolor = 0.106, 0.106, 0.184, 1
        return FRDScreenManager()


if __name__ == '__main__':
    FRDApp().run()
