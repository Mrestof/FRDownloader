from functions import parse

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.properties import ListProperty


# Screens
class FRDScreenManager(ScreenManager):
    pass


class FRDMain(Screen):
    pass


class FRDBrowse(Screen):

    def update_grid(self):
        data = parse(self.sort, self.search, self.page, self.amount, self.days)
        data_packs = zip(*data.values())

        grid = self.ids['items']
        info = self.ids['page_info']

        info_last = self.page * self.amount
        info_first = info_last - self.amount + 1
        info.text = f'showed {info_first}-{info_last}\nitems'

        grid.clear_widgets()

        for _ in range(3):
            grid.add_widget(Widget())

        for tile in data_packs:
            item = FRDItem()

            item.logo = tile[0]
            item.rating = tile[1]
            item.title = tile[2]
            item.author = tile[3]
            item.item_id = tile[4]

            grid.add_widget(item)


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


class FRDItem(BoxLayout):
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
