"""
Lifegame

Use bit to represent status may be more efficient but, nah.
"""
import argparse
import os
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
    fps: float = 60.0

    __symbols: tuple[str, str]
    __frame: np.ndarray
    __prev: np.ndarray
    __loc: np.ndarray
    __cache: list[str] = []

    def __init__(
        self,
        shape: Sequence[int],
        symbol_type: Literal['alpha', 'block', 'digit', 'emoji']
    ) -> None:
        self.shape = (shape[0], shape[1])
        self.__frame = np.random.choice((0, 1), self.shape)
        self.__prev = self.__frame.copy()
        self.__loc = np.empty(2, dtype=np.int8)
        self.set_symbols(symbol_type)

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

    def print(self, *arg, **kwargs) -> None:
        self.__cache.clear()
        for row in self.__frame:
            self.__cache.append(''.join(self.__symbols[col] for col in row))
        print('\n'.join(self.__cache), *arg, **kwargs)

    def generate(self) -> None:
        for index, is_alive in np.ndenumerate(self.__prev):
            count = 0
            for rloc in self.RLOCS:
                for i in range(2):
                    self.__loc[i] = (index[i] + rloc[i]) % self.__prev.shape[i]
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
            os.system('clear')
            self.print()
            self.generate()
            sleep(frame_duration)


def main() -> None:
    parser = argparse.ArgumentParser('Life Game')

    parser.add_argument(
        '--nrows',
        default=32,
        type=int,
        metavar=''
    )

    parser.add_argument(
        '--ncols',
        default=32,
        type=int,
        metavar=''
    )

    parser.add_argument('--fps', default=60, type=int, metavar='')

    parser.add_argument(
        '--symbols',
        default='block',
        choices=('alpha', 'block', 'digit', 'emoji'),
        metavar=''
    )

    args = parser.parse_args()
    
    lifegame = LifeGame((args.nrows, args.ncols), args.symbols)
    lifegame.fps = args.fps
    lifegame.run()


if __name__ == '__main__':
    main()
