import argparse
import asyncio
import subprocess
from random import choice
from textwrap import indent
from typing import Literal, NamedTuple, Sequence

import numpy as np
from numpy.typing import NDArray

try:
    from .const import SYMBOLS
    from .models.frame import RevertibleFrame
except ImportError:
    from const import SYMBOLS
    from models.frame import RevertibleFrame


class Cell:

    dead: str
    alive: str

    def __init__(
        self,
        type: Literal['alpha', 'binary', 'block', 'emoji', 'legacy'] = 'block'
    ) -> None:
        for k, v in SYMBOLS[type.strip().lower()].items():
            if isinstance(v, list):
                v = choice(v)
            if k == 'dead':
                self.dead = v
            elif k == 'alive':
                self.alive = v


class Padding(NamedTuple):

    top: str
    left: str


class LifeGame:

    RESET_CURSOR = '\033[1;1H'

    frame_duration: float

    __cell: Cell
    __frame: RevertibleFrame
    __padding: Padding
    __locs: tuple[NDArray, ...]
    __rlocs: tuple[NDArray, ...]
    __repr_cache: NDArray
    __print_queue: asyncio.Queue[str]

    def __init__(
        self,
        nrows: int = 32,
        ncols: int = 32,
        *,
        cell: Literal['alpha', 'binary', 'block', 'emoji', 'legacy'] = 'block',
        fps: int | float = 24,
        row_offset: int = 1,
        col_offset: int = 2,
        seed: int | None = None
    ) -> None:
        self.__cell = Cell(cell)
        self.__frame = RevertibleFrame((nrows, ncols), np.bool_)
        shape = self.__frame.shape
        self.__frame.prev[:] = np.random.randint(0, 2, shape, np.bool_)
        self.frame_duration = 1 / fps
        self.__padding = Padding('\n' * row_offset, ' ' * col_offset)
        if seed is not None:
            self.seed = seed
        loc_dtype = np.min_scalar_type(np.max(shape))
        self.__locs = np.ix_(np.empty(3, loc_dtype), np.empty(3, loc_dtype))
        self.__rlocs = np.ix_([-1, 0, 1], [-1, 0, 1])
        self.__repr_cache = np.empty(shape, dtype='<U2')
        self.__print_queue = asyncio.Queue()

    @property
    def cell(self) -> Cell:
        return self.__cell

    @property
    def frame(self) -> RevertibleFrame:
        self.__frame

    @property
    def seed(self) -> int:
        return np.random.get_state()[1][0]  # type: ignore

    @seed.setter
    def seed(self, __value: int) -> None:
        np.random.seed(__value)

    async def sleep(self) -> None:
        await asyncio.sleep(self.frame_duration)

    def generate(self) -> None:
        current, next = self.__frame.prev, self.__frame.frame
        shape = self.__frame.shape
        for index, is_alive in np.ndenumerate(current):
            self.__locs[0][:] = (index[0] + self.__rlocs[0]) % shape[0]
            self.__locs[1][:] = (index[1] + self.__rlocs[1]) % shape[1]
            count = current[self.__locs].sum() - is_alive
            if (not is_alive) and (count == 3):
                next[index] = 1
            elif is_alive and (count not in {2, 3}):
                next[index] = 0

    async def repr(self) -> None:
        self.generate()
        current = self.__frame.prev
        self.__repr_cache[current] = self.cell.alive
        self.__repr_cache[~current] = self.cell.dead
        self.__frame.record()
        await self.__print_queue.put(
            '\n'.join(''.join(row) for row in self.__repr_cache)
        )

    async def print(self) -> None:
        repr_ = await self.__print_queue.get()
        padded = self.__padding.top + indent(repr_, self.__padding.left)
        print(self.RESET_CURSOR + padded)

    async def _run(self) -> None:
        subprocess.run('clear || cls', shell=True)
        while True:
            await asyncio.gather(self.sleep(), self.repr(), self.print())

    def run(self) -> None:
        asyncio.run(self._run())


def main(args: Sequence | None = None) -> None:

    HELP = {
        'nrows': 'number of rows',
        'ncols': 'number of columns',
        'cell': 'specify symbol pair to represent cell status (dead / alive)',
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
        choices=('alpha', 'binary', 'block', 'emoji', 'legacy'),
        help=HELP['cell']
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
