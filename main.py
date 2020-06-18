import requests
from functions import parse, get_link, download_and_place

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
    page: int
    last_page: int

    def update_grid(self):
        info = self.ids['page_info']
        grid = self.ids['items']
        page_control = self.ids['page_control']
        prev_page = self.ids['prev_page']
        next_page = self.ids['next_page']

        # disable possibility to go to the 0's page
        if self.page == 1:
            prev_page.disabled = True
        else:
            prev_page.disabled = False

        # parse data from steam workshop
        try:
            data = parse(self.sort, self.search, self.page, self.amount, self.days)
        except requests.exceptions.ConnectionError as err:
            print(err)
            grid.clear_widgets()

            popup = FRDPopup(title='Connection Error!')
            popup.text = 'Check your network connection and try again later.'
            popup.open()

            return 'Can\'t load the items because of connection issues'

        # make list of lists for every character
        data_packs = list(zip(*data['items'].values()))

        if not data_packs:
            popup = FRDPopup(title='Search Error!')
            popup.text = 'Can\'t find any items with such search parameters.'
            popup.open()

            return 'No data returned from parse function'

        self.last_page = data['additional']['last_page']

        # disable possibility to go to the page higher than maximum
        if self.last_page:
            page_control.disabled = False
            print(self.page, self.last_page)
            if self.page == self.last_page:
                next_page.disabled = True
            else:
                next_page.disabled = False
        else:
            page_control.disabled = True

        info.text = f'showed\n{data["additional"]["items_range"]}\nitems'

        # clear grid from previous items and place new from the data_packs list
        grid.clear_widgets()

        # little kludge for occasions in which on the page are only 1 or 2 items
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

    def go_to(self, page):
        # check if page is an integer
        try:
            page = int(page)
        except ValueError as err:
            print(err)

            popup = FRDPopup(title='Value Error!')
            popup.text = 'Number of the page must be an integer, like 12.'
            popup.open()

            return 'Error occurred, can\'t continue'

        # check if page is in the acceptable range
        if 0 < page <= self.last_page:
            if page != self.page:
                self.page = page
                self.update_grid()
        else:
            popup = FRDPopup(title='Value Error!')
            popup.text = f'Number of the page must be in range from 1 to {self.last_page}.'
            popup.open()


# todo make an FRDMyCollectionManager screen
# todo make an FRDSettings screen


# Widgets
class FRDButton(Button):
    pass


class FRDSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # change default option class of the spinner to custom
        self.option_cls = FRDSpinnerOption


class FRDSpinnerOption(SpinnerOption):
    pass


class FRDItem(BoxLayout):

    def add_to_collection(self, path: str):
        # get link for archive to download, check for some exceptions, try to download the item and throw the
        # popup with status message
        if path:
            try:
                download_link = get_link(self.item_id)
            except requests.exceptions.ConnectionError as err:
                print(err)
                popup = FRDPopup(title='Connection Error!')
                popup.text = 'Check your internet connection and try again later.'
                popup.open()
            except AssertionError as err:
                print(err)
                popup = FRDPopup(title='Server Error!')
                popup.text = 'Something went wrong on the server, try again later.'
                popup.open()
            else:
                info = download_and_place(download_link, path, self.item_id)
                key = list(info.keys())[0]

                if key == "Success":
                    popup = FRDPopup(title='Success!')
                    popup.text = info['Success']
                else:
                    popup = FRDPopup(title=f'{key}!')
                    popup.text = info[key]

                popup.open()
        else:
            popup = FRDPopup(title='Path Error!')
            popup.text = 'Path of the game not found, enter it on settings page.'
            popup.open()


class FRDPopup(Popup):
    pass


# App
class FRDApp(App):
    path = ''
    dark_blue = ListProperty(DB_color)
    light_blue = ListProperty(LB_color)
    dark_purple = ListProperty(DP_color)
    pink = ListProperty(P_color)

    def build(self):
        # set the background color of the window
        Window.clearcolor = DP_color
        return FRDScreenManager()


if __name__ == '__main__':
    FRDApp().run()
