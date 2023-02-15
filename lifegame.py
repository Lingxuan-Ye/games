"""
Lifegame

Use bit to represent status may be more efficient but, nah.
"""
import argparse
import asyncio
import subprocess
from random import choice
from typing import Literal, Sequence

import numpy as np


class LifeGame:

    RLOCS = np.array([[x, y] for x in (-1, 0, 1) for y in (-1, 0, 1) if x | y])
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
    frames_per_second: float

    __symbols: tuple[str, str]
    __row_offset: int
    __top_padding: str
    __col_offset: int
    __left_padding: str

    __next_frame: np.ndarray
    __current_frame: np.ndarray
    __loc: np.ndarray
    __to_print: list[str]

    def __init__(
        self,
        nrows: int = 32,
        ncols: int = 32,
        frames_per_second: float = 24.0,
        symbol_type: Literal['alpha', 'block', 'digit', 'emoji'] = 'block',
        row_offset: int = 1,
        col_offset: int = 2
    ) -> None:

        self.shape = (nrows, ncols)
        self.frames_per_second = frames_per_second
        self.row_offset = row_offset
        self.col_offset = col_offset

        self.set_symbols(symbol_type)

        self.__current_frame = np.random.choice((0, 1), self.shape)
        self.__next_frame = self.__current_frame.copy()
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
    def row_offset(self) -> int:
        return self.__row_offset

    @row_offset.setter
    def row_offset(self, __value: int) -> None:
        self.__top_padding = '\n' * __value
        self.__row_offset = __value

    @property
    def col_offset(self) -> int:
        return self.__col_offset

    @col_offset.setter
    def col_offset(self, __value: int) -> None:
        self.__left_padding = ' ' * __value
        self.__col_offset = __value

    async def generate(self) -> None:
        for index, is_alive in np.ndenumerate(self.__current_frame):
            count = 0
            for rloc in self.RLOCS:
                self.__loc[:] = (index + rloc) % self.shape
                if self.__current_frame[*self.__loc]:
                    count += 1
            if (not is_alive) and (count == 3):
                self.__next_frame[index] = 1
            elif is_alive and (count not in {2, 3}):
                self.__next_frame[index] = 0

    @staticmethod
    async def __print_async(message):
        await asyncio.get_event_loop().run_in_executor(None, print, message)

    async def print(self) -> None:
        self.__to_print.clear()
        for row in self.__current_frame:
            self.__to_print.append(
                self.__left_padding + ''.join(self.__symbols[i] for i in row)
            )
        message = self.__top_padding + '\n'.join(self.__to_print)
        await self.__print_async(message)

    async def __run_async(self) -> None:
        frame_duration = 1 / self.frames_per_second
        while True:
            subprocess.run('clear || cls', shell=True)
            await asyncio.gather(
                self.generate(),
                self.print(),
                asyncio.sleep(frame_duration)
            )
            self.__current_frame[:] = self.__next_frame

    def run(self) -> None:
        asyncio.run(self.__run_async())


def main() -> None:

    parser = argparse.ArgumentParser('Life Game')

    parser.add_argument(
        '--nrows',
        type=int,
        help='number of rows',
        metavar=''
    )

    parser.add_argument(
        '--ncols',
        type=int,
        help='number of columns',
        metavar=''
    )

    parser.add_argument(
        '--fps',
        type=float,
        help='frames per second',
        metavar=''
    )

    parser.add_argument(
        '--symbol-type',
        choices=('alpha', 'block', 'digit', 'emoji'),
        help='symbols to represent status (dead / alive)',
        metavar=''
    )

    parser.add_argument(
        '--row-offset',
        type=int,
        help='margin width to the top',
        metavar=''
    )

    parser.add_argument(
        '--col-offset',
        type=int,
        help='margin width to the left',
        metavar=''
    )

    args = dict(filter(
        lambda x: x[1] is not None,
        parser.parse_args()._get_kwargs()
    ))

    LifeGame(**args).run()


if __name__ == '__main__':
    main()
