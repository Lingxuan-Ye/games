"""
Lifegame

Use bit to represent status may be more efficient but, nah.
"""
import argparse
import asyncio
from random import choice
from typing import Literal

import numpy as np


class LifeGame:

    RLOCS = np.array(
        [[x, y] for x in (-1, 0, 1) for y in (-1, 0, 1) if x | y],
        dtype=np.int8
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

    shape: np.ndarray
    frames_per_second: int | float

    __symbols: tuple[str, str]
    __row_offset: int
    __top_padding: str
    __col_offset: int
    __left_padding: str

    __next_frame: np.ndarray
    __current_frame: np.ndarray
    __locs: np.ndarray
    __to_print: list[str]

    def __init__(
        self,
        nrows: int = 32,
        ncols: int = 32,
        frames_per_second: int | float = 10,
        symbol_type: Literal['alpha', 'block', 'digit', 'emoji'] = 'block',
        row_offset: int = 1,
        col_offset: int = 2
    ) -> None:

        self.shape = np.array([nrows, ncols])
        self.frames_per_second = frames_per_second
        self.row_offset = row_offset
        self.col_offset = col_offset

        self.set_symbols(symbol_type)

        init_frame = np.random.randint(0, 2, self.shape, dtype=np.int8)
        self.__current_frame = init_frame
        self.__next_frame = init_frame.copy()
        self.__locs = np.empty_like(self.RLOCS)
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

    async def print(self, *args, **kwargs) -> None:
        process = await asyncio.create_subprocess_shell('clear || cls')
        await process.wait()
        self.__to_print.clear()
        for row in self.__current_frame:
            self.__to_print.append(
                self.__left_padding + ''.join(self.__symbols[i] for i in row)
            )
        message = self.__top_padding + '\n'.join(self.__to_print)
        print(message, *args, **kwargs)

    async def generate(self) -> None:
        for index, is_alive in np.ndenumerate(self.__current_frame):
            self.__locs[:] = (
                np.array([index], dtype=np.int8) + self.RLOCS
            ) % self.shape.reshape(1, 2)  # mod in case index out of range
            count = self.__current_frame[tuple(self.__locs.T)].sum()
            if (not is_alive) and (count == 3):
                self.__next_frame[index] = 1
            elif is_alive and (count not in {2, 3}):
                self.__next_frame[index] = 0

    async def __run(self) -> None:
        frame_duration = 1 / self.frames_per_second
        while True:
            await asyncio.gather(
                asyncio.sleep(frame_duration),
                self.print(),
                self.generate()
            )
            self.__current_frame[:] = self.__next_frame

    def run(self) -> None:
        asyncio.run(self.__run())


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
        metavar='',
        dest='frames_per_second'
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
