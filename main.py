from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.properties import ListProperty


# Screens
class FRDScreenManager(ScreenManager):
    pass


class FRDMain(Screen):
    pass


class FRDBrowse(Screen):
    pass


# todo make an FRDMyCollectionManager screen


# Widgets
class FRDButton(Button):
    pass


class FRDApp(App):
    dark_blue = ListProperty([0.086, 0.141, 0.278, 1])
    light_blue = ListProperty([0.122, 0.251, 0.408, 1])
    dark_purple = ListProperty([0.106, 0.106, 0.184, 1])
    pink = ListProperty([0.894, 0.247, 0.353, 1])

    def build(self):
        return FRDScreenManager()


if __name__ == '__main__':
    FRDApp().run()
