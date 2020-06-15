import requests
from functions import parse

from kivy.app import App
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.properties import ListProperty

# Consts
DB_color = 0.086, 0.141, 0.278, 1
LB_color = 0.122, 0.251, 0.408, 1
DP_color = 0.106, 0.106, 0.184, 1
P_color = 0.894, 0.247, 0.353, 1


# Screens
class FRDScreenManager(ScreenManager):
    pass


class FRDMain(Screen):
    pass


class FRDBrowse(Screen):

    last_page: int

    def update_grid(self):
        info = self.ids['page_info']
        grid = self.ids['items']
        page_control = self.ids['page_control']
        prev_page = self.ids['prev_page']
        next_page = self.ids['next_page']

        if self.page == 1:
            prev_page.disabled = True
        else:
            prev_page.disabled = False

        try:
            data = parse(self.sort, self.search, self.page, self.amount, self.days)
        except requests.exceptions.ConnectionError as err:
            print(err)
            grid.clear_widgets()

            popup = FRDPopup(title='Connection Error!')
            popup.text = 'Check your network connection and try again later.'
            popup.open()

            return 'Can\'t load the items because of connection issues'

        data_packs = list(zip(*data['items'].values()))

        if not data_packs:
            popup = FRDPopup(title='Search Error!')
            popup.text = 'Can\'t find any items with such search parameters'
            popup.open()

            return 'No data returned from parse function'

        self.last_page = data['additional']['last_page']

        if self.last_page:
            page_control.disabled = False
            print(self.page, self.last_page)
            if self.page == self.last_page:
                next_page.disabled = True
            else:
                next_page.disabled = False
        else:
            page_control.disabled = True

        info.text = f'showed {data["additional"]["items_range"]}\nitems'

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


class FRDPopup(Popup):
    pass


# App
class FRDApp(App):
    dark_blue = ListProperty(DB_color)
    light_blue = ListProperty(LB_color)
    dark_purple = ListProperty(DP_color)
    pink = ListProperty(P_color)

    def build(self):
        Window.clearcolor = DP_color
        return FRDScreenManager()


if __name__ == '__main__':
    FRDApp().run()
