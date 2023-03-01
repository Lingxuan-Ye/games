import abc
from types import EllipsisType
from typing import Any, Generic, Iterable, MutableSequence, Self, Sequence, TypeVar, final

import numpy as np
from numpy.typing import NDArray


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
_0DIndex = MutableSequence | NDArray | int | slice | EllipsisType | None
_NDIndex = tuple[_0DIndex | tuple, ...]
_Index = _0DIndex | _NDIndex
_Value = np.number | NDArray

T = TypeVar('T', bound=np.number)


class _BaseFrame(abc.ABC, Generic[T]):

    dtype: type[T]

    _shape: Shape
    _frame: NDArray[T]

    def __init__(
        self,
        shape: Iterable[int],
        dtype: type[T] | None = None
    ) -> None:
        self._shape = Shape(shape)
        if dtype is not None:
            self.dtype = dtype
        self.init_frame()

    @property
    def shape(self) -> Shape:
        return self._shape

    @property
    def ndim(self) -> int:
        return len(self._shape)

    @property
    def frame(self) -> NDArray[T]:
        return self._frame

    @abc.abstractmethod
    def __getitem__(self, index: _Index, /) -> Any:
        ...

    @abc.abstractmethod
    def __setitem__(self, index: _Index, value: Any, /) -> None:
        ...

    @final
    def resize(self, shape: Iterable[int]) -> Self:
        self._shape = Shape(shape)
        self._frame = np.resize(self._frame, self._shape)
        return self

    @abc.abstractmethod
    def init_frame(self) -> Self:
        ...

    @final
    def set_frame(self, frame: NDArray[T]) -> Self:
        if self._shape == frame.shape:
            self._frame[:] = frame
            return self
        self._shape = Shape(frame.shape)
        self._frame = frame.copy()
        return self


class _SubcriptableFrame(_BaseFrame):

    @final
    def __getitem__(self, index: _Index, /) -> _Value:
        return self._frame[self.mod_index(index)]

    @final
    def __setitem__(self, index: _Index, value: _Value, /) -> None:
        self._frame[self.mod_index(index)] = value

    @final
    def mod_index(self, index: _Index) -> _Index:
        if isinstance(index, tuple):
            return tuple(self.__mod_index(i, ax) for ax, i in enumerate(index))
        return self.__mod_index(index, axis=0)

    @final
    def __mod_index(self, index: _Index, axis: int) -> _Index:
        if isinstance(index, MutableSequence | NDArray):
            return np.asarray(index) % self._shape[axis]
        if isinstance(index, int):
            return index % self._shape[axis]
        if isinstance(index, slice):
            return slice(
                index.start % self._shape[axis],
                index.stop % self._shape[axis],
                index.step % self._shape[axis]
            )
        return index


class Frame(_SubcriptableFrame):

    def init_frame(self) -> Self:
        self._frame = np.empty(self._shape, self.dtype)
        return self


U = TypeVar('U', bound=np.unsignedinteger)


class RGB(Frame, Generic[U]):

    dtype = np.uint8

    def __init__(
        self,
        shape: Iterable[int],
        dtype: type[U] | None = None
    ) -> None:
        super().__init__((*shape, 3), dtype)

    @property
    def ndim(self) -> int:
        return len(self._shape) - 1

    @property
    def red(self) -> NDArray[U]:
        return self._frame[..., 0]

    @property
    def green(self) -> NDArray[U]:
        return self._frame[..., 1]

    @property
    def blue(self) -> NDArray[U]:
        return self._frame[..., 2]

    R, G, B = red, green, blue


class RGBA(RGB[U]):

    def __init__(
        self,
        shape: Iterable[int],
        dtype: type[U] | None = None
    ) -> None:
        super(RGB, self).__init__((*shape, 4), dtype)

    @property
    def alpha(self) -> NDArray[U]:
        return self._frame[..., 3]

    A = alpha


class RevertibleFrame(Frame, Generic[T]):

    _prev: NDArray[T]

    @property
    def prev(self) -> NDArray[T]:
        return self._prev

    def init_frame(self) -> Self:
        super().init_frame()
        self._prev = self._frame.copy()
        return self

    @final
    def record(self) -> Self:
        self._prev[:] = self._frame
        return self

    @final
    def revert(self) -> Self:
        self._frame[:] = self._prev
        return self


class RevertibleRGB(RGB[U], RevertibleFrame):

    @property
    def prev_red(self) -> NDArray[U]:
        return self._prev[..., 0]

    @property
    def prev_green(self) -> NDArray[U]:
        return self._prev[..., 1]

    @property
    def prev_blue(self) -> NDArray[U]:
        return self._prev[..., 2]


class RevertibleRGBA(RGBA[U], RevertibleRGB):

    @property
    def prev_alpha(self) -> NDArray[U]:
        return self._prev[..., 3]


class BitFrame(Frame):

    pass  # TODO
