from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

from layla_engine import LaylaEngine


Window.clearcolor = (0.01, 0.005, 0.02, 1)


class ChatScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=8,
            padding=10,
            **kwargs
        )

        self.layla = LaylaEngine()

        self.chat = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8
        )

        self.chat.bind(
            minimum_height=self.chat.setter("height")
        )

        scroll = ScrollView()
        scroll.add_widget(self.chat)

        self.add_widget(scroll)

        bottom = BoxLayout(
            size_hint_y=None,
            height=55,
            spacing=8
        )

        self.input_box = TextInput(
            hint_text="Message Layla...",
            multiline=False,
            font_size=18
        )

        self.input_box.bind(
            on_text_validate=self.send_message
        )

        send_button = Button(
            text="Send",
            size_hint_x=None,
            width=90
        )

        send_button.bind(
            on_press=self.send_message
        )

        bottom.add_widget(self.input_box)
        bottom.add_widget(send_button)

        self.add_widget(bottom)

    def add_message(self, speaker, message):
        label = Label(
            text=f"{speaker}: {message}",
            size_hint_y=None,
            text_size=(None, None),
            halign="left",
            valign="top",
            padding=(8, 8)
        )

        label.bind(
            texture_size=lambda instance, size:
            setattr(instance, "height", size[1] + 16)
        )

        self.chat.add_widget(label)

    def send_message(self, *args):
        text = self.input_box.text.strip()

        if not text:
            return

        self.input_box.text = ""

        self.add_message("You", text)

        if text.lower() == "exit":
            App.get_running_app().stop()
            return

        try:
            answer = self.layla.chat(text)
        except Exception as error:
            answer = f"Error: {error}"

        self.add_message("Layla", answer)


class LaylaApp(App):

    title = "Layla"

    def build(self):
        return ChatScreen()


if __name__ == "__main__":
    LaylaApp().run()
