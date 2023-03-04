import argparse
import asyncio
import subprocess
from random import choice, sample
from textwrap import indent
from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.signal import convolve2d

try:
    from .const import ANSI_CODE, SYMBOLS
    from .models.frame import RevertibleFrame
except ImportError:
    from const import ANSI_CODE, SYMBOLS
    from models.frame import RevertibleFrame

CellStyle = Literal['alpha', 'binary', 'block', 'emoji', 'legacy', 'palette']


class Cell:

    dead: str
    alive: str

    def __init__(self, style: CellStyle) -> None:
        style_str = str(style).strip().lower()
        if style_str == 'palette':
            dead, alive = sample(list(ANSI_CODE['background'].values()), 2)
            self.dead = dead + '  ' + ANSI_CODE['charstyle']['reset']
            self.alive = alive + '  ' + ANSI_CODE['charstyle']['reset']
            return
        for k, v in SYMBOLS[style_str].items():
            v = choice(v)
            if v == 'block':
                v *= 2
            if k == 'dead':
                self.dead = v
            elif k == 'alive':
                self.alive = v


class Padding:

    __top: str
    __left: str

    def __init__(self, top_margin: int, left_margin: int) -> None:
        self.__top = '\n' * top_margin
        self.__left = ' ' * left_margin

    @property
    def top(self) -> str:
        return self.__top

    @property
    def left(self) -> str:
        return self.__left


class LifeGame:

    KERNEL = np.array([[1, 1, 1], [1, -9, 1], [1, 1, 1]], dtype=np.int8)
    KEEP_ALIVE = np.array([-7, -6], dtype=np.int8)

    frame_duration: float

    __cell: Cell
    __frame: RevertibleFrame
    __padding: Padding
    __render_cache: NDArray
    __print_queue: asyncio.Queue[str]

    def __init__(
        self,
        nrows: int = 32,
        ncols: int = 32,
        *,
        cell_style: CellStyle = 'palette',
        fps: float = 24.0,
        row_offset: int = 1,
        col_offset: int = 2,
        seed: int | None = None
    ) -> None:
        if seed is not None:
            self.seed = seed
        self.__cell = Cell(cell_style)
        self.__frame = RevertibleFrame((nrows, ncols), np.bool_)
        shape = self.__frame.shape
        self.__frame.prev[:] = np.random.randint(0, 2, shape, np.bool_)
        self.__frame.revert()
        self.fps = fps
        self.__padding = Padding(row_offset, col_offset)
        self.__render_cache = np.empty(shape, dtype='<U11')
        self.__print_queue = asyncio.Queue(8)

    @property
    def cell(self) -> Cell:
        return self.__cell

    @property
    def frame(self) -> RevertibleFrame:
        self.__frame

    @property
    def fps(self) -> float:
        return 1 / self.frame_duration

    @fps.setter
    def fps(self, __value: float) -> None:
        self.frame_duration = 1 / __value

    @property
    def seed(self) -> int:
        return np.random.get_state()[1][0]  # type: ignore

    @seed.setter
    def seed(self, __value: int) -> None:
        np.random.seed(__value)

    def generate(self) -> None:
        current, next_ = self.__frame.prev, self.__frame.frame
        result = convolve2d(current, self.KERNEL, mode='same', boundary='wrap')
        next_[result == 3] = True
        next_[(~np.isin(result, self.KEEP_ALIVE)) & (result < 0)] = False

    async def render(self) -> None:
        while True:
            self.generate()
            current = self.__frame.prev
            self.__render_cache[:] = self.cell.dead
            self.__render_cache[current] = self.cell.alive
            self.__frame.record()
            await self.__print_queue.put(
                '\n'.join(''.join(row) for row in self.__render_cache)
            )
            await asyncio.sleep(0)

    async def print(self) -> None:
        while True:
            rendered = await self.__print_queue.get()
            padded = self.__padding.top + indent(rendered, self.__padding.left)
            print(ANSI_CODE['cursor']['reset'] + padded)
            self.__print_queue.task_done()
            await asyncio.sleep(self.frame_duration)

    async def _run(self) -> None:
        await asyncio.gather(self.render(), self.print())

    def run(self) -> None:
        subprocess.run('clear || cls', shell=True)
        asyncio.run(self._run())


def main(args: Sequence | None = None) -> None:

    HELP = {
        'nrows': 'number of rows',
        'ncols': 'number of columns',
        'cell': 'specify cell style',
        'fps': 'frames per second',
        'row-offset': 'margin width to the top',
        'col-offset': 'margin width to the left',
        'seed': 'set seed (this does not affect emoji selection)'
    }

    parser = argparse.ArgumentParser('Life Game')

    parser.add_argument('-r', '--nrows', type=int, help=HELP['nrows'])

    parser.add_argument('-c', '--ncols', type=int, help=HELP['ncols'])

    parser.add_argument(
        '--cell',
        choices=('alpha', 'binary', 'block', 'emoji', 'legacy', 'palette'),
        help=HELP['cell'],
        dest='cell_style'
    )

    parser.add_argument('--fps', type=float, help=HELP['fps'])

    parser.add_argument(
        '-y', '--row-offset', type=int, help=HELP['row-offset']
    )

    parser.add_argument(
        '-x', '--col-offset', type=int, help=HELP['col-offset']
    )

    parser.add_argument('-s', '--seed', type=int, help=HELP['seed'])

    LifeGame(
        **{
            option: value
            for option, value in parser.parse_args(args)._get_kwargs()
            if value is not None
        }
    ).run()


if __name__ == '__main__':
    main()
