import abc
from typing import Any, Iterable, MutableSequence, Self, Sequence, final

import numpy as np


class Shape(tuple[int]):

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Sequence | np.ndarray):
            return False
        if len(self) != len(__o):
            return False
        for i, j in enumerate(self):
            if j != __o[i]:
                return False
        return True

    def __repr__(self) -> str:
        return type(self).__name__ + super().__repr__()


# None for `np.newaxis`
_0DIndex = MutableSequence | np.ndarray | int | slice | ellipsis | None
_NDIndex = tuple[_0DIndex | tuple, ...]
_Index = _0DIndex | _NDIndex
_Value = np.number | np.ndarray


class _BaseFrame(abc.ABC):

    dtype: type[np.number]

    __shape: Shape
    __frame: np.ndarray

    def __init__(
        self,
        shape: Iterable[int],
        dtype: type[np.number] | None = None
    ) -> None:
        self.__shape = Shape(shape)
        if dtype is not None:
            self.dtype = dtype
        self.init_frame()

    @property
    def shape(self) -> Shape:
        return self.__shape

    @property
    def ndim(self) -> int:
        return len(self.__shape)

    @property
    def frame(self) -> np.ndarray:
        return self.__frame

    @abc.abstractmethod
    def __getitem__(self, index: _Index, /) -> Any:
        ...

    @abc.abstractmethod
    def __setitem__(self, index: _Index, value: Any, /) -> None:
        ...

    @final
    def resize(self, shape: Iterable[int]) -> Self:
        self.__shape = Shape(shape)
        self.__frame = np.resize(self.__frame, self.__shape)
        return self

    @abc.abstractmethod
    def init_frame(self) -> Self:
        ...

    @final
    def set_frame(self, frame: np.ndarray) -> Self:
        if self.__shape == frame.shape:
            self.__frame[:] = frame
            return self
        self.__shape = Shape(frame.shape)
        self.__frame = frame.copy()
        return self


class _SubcriptableFrame(_BaseFrame):

    @final
    def __getitem__(self, index: _Index, /) -> _Value:
        return self.__frame[self.mod_index(index)]

    @final
    def __setitem__(self, index: _Index, value: _Value, /) -> None:
        self.__frame[self.mod_index(index)] = value

    @final
    def mod_index(self, index: _Index) -> _Index:
        if isinstance(index, tuple):
            return tuple(self.__mod_index(i, ax) for ax, i in enumerate(index))
        return self.__mod_index(index, axis=0)

    @final
    def __mod_index(self, index: _Index, axis: int) -> _Index:
        if isinstance(index, MutableSequence | np.ndarray):
            return np.asarray(index) % self.__shape[axis]
        if isinstance(index, int):
            return index % self.__shape[axis]
        if isinstance(index, slice):
            return slice(
                index.start % self.__shape[axis],
                index.stop % self.__shape[axis],
                index.step % self.__shape[axis]
            )
        return index


class Frame(_SubcriptableFrame):

    def init_frame(self) -> Self:
        self.__frame = np.empty(self.__shape, self.dtype)
        return self


class RGB(Frame):

    dtype = np.uint8

    def __init__(
        self,
        shape: Iterable[int],
        dtype: type[np.unsignedinteger] | None = None
    ) -> None:
        super().__init__((*shape, 3), dtype)

    @property
    def ndim(self) -> int:
        return len(self.__shape) - 1

    @property
    def red(self) -> np.ndarray:
        return self.__frame[..., 0]

    @property
    def green(self) -> np.ndarray:
        return self.__frame[..., 1]

    @property
    def blue(self) -> np.ndarray:
        return self.__frame[..., 2]

    R, G, B = red, green, blue


class RGBA(RGB):

    def __init__(
        self,
        shape: Iterable[int],
        dtype: type[np.unsignedinteger] | None = None
    ) -> None:
        super(RGB, self).__init__((*shape, 4), dtype)

    @property
    def alpha(self) -> np.ndarray:
        return self.__frame[..., 3]

    A = alpha


class RevertibleFrame(Frame):

    __prev: np.ndarray

    @property
    def prev(self) -> np.ndarray:
        return self.__prev

    def init_frame(self) -> Self:
        super().init_frame()
        self.__prev = self.__frame.copy()
        return self

    @final
    def record(self) -> Self:
        self.__prev[:] = self.__frame
        return self

    @final
    def revert(self) -> Self:
        self.__frame[:] = self.__prev
        return self


class RevertibleRGB(RGB, RevertibleFrame):

    @property
    def prev_red(self) -> np.ndarray:
        return self.__prev[..., 0]

    @property
    def prev_green(self) -> np.ndarray:
        return self.__prev[..., 1]

    @property
    def prev_blue(self) -> np.ndarray:
        return self.__prev[..., 2]


class RevertibleRGBA(RGBA, RevertibleRGB):

    @property
    def prev_alpha(self) -> np.ndarray:
        return self.__prev[..., 3]


class BitFrame(Frame):

    pass  # TODO
