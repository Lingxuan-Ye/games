"""
Lifegame

Use bit to represent status may be more efficient but, nah.
"""
import argparse
import subprocess
from random import choice
from time import sleep
from typing import Literal, Sequence

import numpy as np


class LifeGame:

    RLOCS = np.array(
        [[x, y] for x in (-1, 0, 1) for y in (-1, 0, 1) if x or y]
    )
    SYMBOLS = {
        'dead': {
            'alpha': 'O',
            'block': '⬜',
            'digit': '0',
            'emoji': '😅😇🤪😴🤢🤮🥶😰😭'
        },
        'alive': {
            'alpha': 'X',
            'block': '⬛',
            'digit': '1',
            'emoji': '🤣🥰😘😋🤗🤤🥵🥳😤'
        }
    }

    shape: tuple[int, int]
    fps: int | float

    __frame: np.ndarray
    __prev: np.ndarray
    __loc: np.ndarray
    __symbols: tuple[str, str]
    __to_print: list[str]

    __margin: int
    __margin_top: str
    __margin_left: str

    def __init__(
        self,
        shape: Sequence[int] = (32, 32),
        symbol_type: Literal['alpha', 'block', 'digit', 'emoji'] = 'block',
        margin: int = 2,
        fps: int | float = 60
    ) -> None:
        self.shape = (shape[0], shape[1])
        self.set_symbols(symbol_type)
        self.margin = margin
        self.fps = fps
        self.__frame = np.random.choice((0, 1), self.shape)
        self.__prev = self.__frame.copy()
        self.__loc = np.empty(2, dtype=np.int8)
        self.__to_print = []

    @property
    def symbols(self) -> tuple[str, str]:
        return self.__symbols

    def set_symbols(
        self,
        type_: Literal['alpha', 'block', 'digit', 'emoji']
    ) -> None:
        type_ = type_.strip().lower()  # type: ignore
        self.__symbols = (
            choice(self.SYMBOLS['dead'][type_]),
            choice(self.SYMBOLS['alive'][type_])
        )

    @property
    def margin(self) -> int:
        return self.__margin

    @margin.setter
    def margin(self, __value: int) -> None:
        self.__margin_top = '\n' * __value
        self.__margin_left = ' ' * __value
        self.__margin = __value

    def print(self, *arg, **kwargs) -> None:
        self.__to_print.clear()
        for row in self.__frame:
            self.__to_print.append(
                self.__margin_left + ''.join(self.__symbols[i] for i in row)
            )
        print(self.__margin_top + '\n'.join(self.__to_print), *arg, **kwargs)

    def generate(self) -> None:
        for index, is_alive in np.ndenumerate(self.__prev):
            count = 0
            for rloc in self.RLOCS:
                self.__loc[:] = (index + rloc) % self.shape
                if self.__prev[*self.__loc]:
                    count += 1
            if (not is_alive) and (count == 3):
                self.__frame[index] = 1
            elif is_alive and (count not in {2, 3}):
                self.__frame[index] = 0
        self.__prev[:] = self.__frame

    def run(self) -> None:
        frame_duration = 1 / self.fps
        while True:
            subprocess.run('clear || cls', shell=True)
            self.print()
            self.generate()
            sleep(frame_duration)


def main() -> None:

    parser = argparse.ArgumentParser('Life Game')

    parser.add_argument(
        '--nrows',
        default=32,
        type=int,
        help='number of rows',
        metavar=''
    )

    parser.add_argument(
        '--ncols',
        default=32,
        type=int,
        help='number of columns',
        metavar=''
    )

    parser.add_argument(
        '--symbols',
        default='block',
        choices=('alpha', 'block', 'digit', 'emoji'),
        help='symbols to represent status (dead / alive)',
        metavar=''
    )

    parser.add_argument(
        '--fps',
        default=60,
        type=int,
        help='frames per second',
        metavar=''
    )

    parser.add_argument(
        '--margin',
        default=2,
        type=int,
        help='margin width',
        metavar=''
    )

    args = parser.parse_args()

    LifeGame(
        shape=(args.nrows, args.ncols),
        symbol_type=args.symbols,
        margin=args.margin,
        fps=args.fps
    ).run()


if __name__ == '__main__':
    main()
