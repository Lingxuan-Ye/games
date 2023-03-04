"""
Lifegame

Use bit to represent status may be more efficient but, nah.
"""
import argparse
import asyncio
import subprocess
from random import choice
from typing import Literal

import numpy as np


class LifeGame:

    SYMBOLS = {
        'dead': {
            'alpha': 'X',
            'block': '⬜',
            'digit': '0',
            'emoji': '😅😇🤪😴🤢🤮🥶😰😭'
        },
        'alive': {
            'alpha': 'O',
            'block': '⬛',
            'digit': '1',
            'emoji': '🤣🥰😘😋🤗🤤🥵🥳😤'
        }
    }
    RLOCS = np.array([(-1, 0, 1)] * 2, dtype=np.int8)

    shape: np.ndarray
    frames_per_second: int | float

    __symbols: tuple[str, str]
    __row_offset: int
    __top_padding: str
    __col_offset: int
    __left_padding: str

    __next_frame: np.ndarray
    __current_frame: np.ndarray
    __to_print: list[str]
    __locs: np.ndarray

    def __init__(
        self,
        nrows: int = 32,
        ncols: int = 32,
        frames_per_second: int | float = 10,
        symbol_type: Literal['alpha', 'block', 'digit', 'emoji'] = 'block',
        row_offset: int = 1,
        col_offset: int = 2,
        seed: int | None = None
    ) -> None:

        self.shape = np.array([nrows, ncols])
        self.frames_per_second = frames_per_second
        self.row_offset = row_offset
        self.col_offset = col_offset
        if seed is not None:
            self.seed = seed
        self.set_symbols(symbol_type)

        init_frame = np.random.randint(0, 2, self.shape, dtype=np.uint8)
        self.__current_frame = init_frame
        self.__next_frame = init_frame.copy()
        self.__to_print = []
        self.__locs = np.empty(
            shape=(2, 3),
            dtype=np.min_scalar_type(np.max(self.shape))
        )

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

    @property
    def seed(self) -> int:
        return np.random.get_state()[1][0]  # type: ignore

    @seed.setter
    def seed(self, __value: int) -> None:
        np.random.seed(__value)

    async def print(self, *args, **kwargs) -> None:
        self.__to_print.clear()
        for row in self.__current_frame:
            self.__to_print.append(
                self.__left_padding + ''.join(self.__symbols[i] for i in row)
            )
        message = self.__top_padding + '\n'.join(self.__to_print)
        print(f'\033[1;1H{message}', *args, **kwargs)

    async def generate(self) -> None:
        for index, is_alive in np.ndenumerate(self.__current_frame):
            self.__locs[:] = (
                np.array(list(index)).reshape(2, 1) + self.RLOCS
            ) % self.shape.reshape(2, 1)  # mod in case index out of range
            count = self.__current_frame[np.ix_(*self.__locs)].sum() - is_alive
            if (not is_alive) and (count == 3):
                self.__next_frame[index] = 1
            elif is_alive and (count not in {2, 3}):
                self.__next_frame[index] = 0

    async def __run(self) -> None:
        frame_duration = 1 / self.frames_per_second
        subprocess.run('clear || cls', shell=True)
        while True:
            await asyncio.gather(
                asyncio.sleep(frame_duration),
                self.print(),
                self.generate()
            )
            self.__current_frame[:] = self.__next_frame

    def run(self) -> None:
        asyncio.run(self.__run())

    @classmethod
    def run_from_command_line(cls) -> None:

        HELP = {
            'nrows': 'number of rows',
            'ncols': 'number of columns',
            'fps': 'frames per second',
            'symbol-type': 'symbols to represent status (dead / alive)',
            'row-offset': 'margin width to the top',
            'col-offset': 'margin width to the left',
            'seed': 'set seed (this does not affect emoji selection)'
        }

        parser = argparse.ArgumentParser('Life Game')

        parser.add_argument(
            '-r',
            '--nrows',
            type=int,
            help=HELP['nrows'],
            metavar=''
        )

        parser.add_argument(
            '-c',
            '--ncols',
            type=int,
            help=HELP['ncols'],
            metavar=''
        )

        parser.add_argument(
            '-f',
            '--fps',
            type=float,
            help=HELP['fps'],
            metavar='',
            dest='frames_per_second'
        )

        parser.add_argument(
            '-s',
            '--symbol-type',
            choices=('alpha', 'block', 'digit', 'emoji'),
            help=HELP['symbol-type'],
            metavar=''
        )

        parser.add_argument(
            '-R',
            '--row-offset',
            type=int,
            help=HELP['row-offset'],
            metavar=''
        )

        parser.add_argument(
            '-C',
            '--col-offset',
            type=int,
            help=HELP['col-offset'],
            metavar=''
        )

        parser.add_argument(
            '-S',
            '--seed',
            type=int,
            help=HELP['seed'],
            metavar=''
        )

        cls(**{
            param: arg
            for param, arg in parser.parse_args()._get_kwargs()
            if arg is not None
        }).run()


if __name__ == '__main__':
    LifeGame.run_from_command_line()
