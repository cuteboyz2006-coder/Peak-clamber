from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

Window.clearcolor = (0.01, 0.005, 0.02, 1)


class ChatScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=8,
            padding=10,
            **kwargs
        )

        # AI engine will be loaded after the interface is created.
        self.layla = None

        self.status_label = Label(
            text="Layla is starting...",
            size_hint_y=None,
            height=48,
            halign="left",
            valign="middle"
        )

        self.status_label.bind(
            size=lambda instance, size:
            setattr(instance, "text_size", size)
        )

        self.add_widget(self.status_label)

        # Chat area
        self.chat = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8
        )

        self.chat.bind(
            minimum_height=self.chat.setter("height")
        )

        self.scroll = ScrollView()
        self.scroll.add_widget(self.chat)
        self.add_widget(self.scroll)

        # Message input
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

        # Load the AI engine after the UI exists.
        try:
            from layla_engine import LaylaEngine

            self.layla = LaylaEngine()

            self.status_label.text = "Layla is ready."

        except Exception as error:

            self.status_label.text = (
                "Layla AI could not start."
            )

            self.add_message(
                "Startup error",
                f"{type(error).__name__}: {error}"
            )

            self.add_message(
                "Next step",
                "Please note the exact error shown above."
            )

    def add_message(self, speaker, message):

        label = Label(
            text=f"{speaker}: {message}",
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=(8, 8)
        )

        label.bind(
            width=lambda instance, width:
            setattr(
                instance,
                "text_size",
                (max(1, width - 16), None)
            )
        )

        label.bind(
            texture_size=lambda instance, size:
            setattr(
                instance,
                "height",
                size[1] + 16
            )
        )

        self.chat.add_widget(label)

        self.chat.height = self.chat.minimum_height

        self.scroll.scroll_y = 0

    def send_message(self, *args):

        message = self.input_box.text.strip()

        if not message:
            return

        self.input_box.text = ""

        self.add_message("You", message)

        if message.lower() == "exit":
            App.get_running_app().stop()
            return

        if self.layla is None:

            self.add_message(
                "Layla",
                "The AI engine did not start. "
                "Please check the Startup error above."
            )

            return

        try:
            answer = self.layla.chat(message)

        except Exception as error:
            answer = (
                f"{type(error).__name__}: {error}"
            )

        self.add_message("Layla", answer)


class LaylaApp(App):

    title = "Layla"

    def build(self):
        return ChatScreen()


if __name__ == "__main__":
    LaylaApp().run()