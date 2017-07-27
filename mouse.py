import win32api, win32con
import os.path

from dragonfly import MappingRule, Function
from dragonfly_loader import Unit, json_parser


class Mouse(Unit):

    def __init__(self, grammar_name="mouse"):
        Unit.__init__(self, grammar_name)
        self.__scrolling = False
        self.__scroll_position = None

    def create_grammar(self, g, t):
        rule = MappingRule(
            mapping={
                t("scroll"): Function(lambda: self.toggle_scroll()),
                t("right_click"): Mouse("right"),
                "\"" + t("left_click") + "|" + t("click") + "|" + t("focus") + "\"": Mouse("left"),
                "\"" + t("double_click") + "|" + t("double") + "|" + t("open") + "|" + t("select") + "\"":  Mouse("left/3, left/3"),
            }
        )
        g.add_rule(rule)
        return True

    def toggle_scroll(self):
        self.__scrolling = not self.__scrolling
        self.__scroll_position = win32api.GetCursorPos()

    def create_callbacks(self):
        def get_scroll_amount(moved):
            if -self.__scroll_threshold < moved < self.__scroll_threshold:
                return 0
            if moved > 0:
                value = moved - self.__scroll_threshold
                return int(self.__scroll_speed * (value * value))
            else:
                value = moved + self.__scroll_threshold
                return int(-self.__scroll_speed * (value * value))

        def call():
            if self.__scrolling:
                x, y = win32api.GetCursorPos()
                dx = x - self.__scroll_position[0]
                dy = y - self.__scroll_position[1]
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, get_scroll_amount(-dy))

        return [(call, 0.01)]

    def load_config(self, config_path):
        default = {
            "scroll_threshold": 3,
            "scroll_speed": 0.003
        }
        data = json_parser.parse_json(os.path.join(config_path, "mouse.json"), default)
        self.__scroll_threshold = data["scroll_threshold"]
        self.__scroll_speed = data["scroll_speed"]


def create_unit():
    return Mouse()
