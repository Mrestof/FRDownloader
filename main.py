from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class FRDRootWidget(BoxLayout):
    pass


class FRDApp(App):
    def build(self):
        return FRDRootWidget()


if __name__ == '__main__':
    FRDApp().run()
