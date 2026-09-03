import tkinter as tk

from libs.theme import BG_CHROME
from libs.gui.config_frame import ConfigFrame
from libs.gui.info_frame import InfoFrame
from libs.gui.train_frame import TrainFrame
from libs.gui.train_config import TrainConfig


class App(tk.Tk):
    """Root window: switches between ConfigFrame, TrainFrame and InfoFrame."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Snake DQN")
        self.configure(bg=BG_CHROME)

        self.current_frame: tk.Frame | None = None
        self.last_config: TrainConfig | None = None

        self._fullscreen = True
        self.attributes("-fullscreen", self._fullscreen)
        self.bind("<Escape>", lambda _event: self.toggle_fullscreen())
        self.bind("<F11>", lambda _event: self.toggle_fullscreen())

        self.show_config()

    def toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    def _swap(self, frame: tk.Frame) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

    def show_config(self) -> None:
        self._swap(ConfigFrame(self, on_start=self.show_training, on_info=self.show_info))

    def show_training(self, config: TrainConfig) -> None:
        self.last_config = config
        self._swap(TrainFrame(self, config, on_menu=self.show_config))

    def show_info(self) -> None:
        self._swap(InfoFrame(self, on_back=self.show_config))


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
