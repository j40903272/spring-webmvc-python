import inspect
from copy import deepcopy
from typing import TypeVar, ClassVar

T = TypeVar("T")
C = ClassVar[T]


class Function(object):
    """Function is a wrap over standard python function."""

    def __init__(self, fn):
        self.fn = fn
        self.signatures = []
        self.register()

    def __call__(self, *args, **kwargs):
        """Overriding the __call__ function which makes the
        instance callable.
        """
        # fetching the function to be invoked from the virtual namespace
        # through the arguments.
        fn = Namespace.get_instance().get(self.fn, *args)
        if not fn:
            raise Exception(
                f"no matching function signature found. \
                signature:[{self.key(args)[0]}]"
            )
        return fn(*args, **kwargs)

    def _register(self, types):
        self.signatures.append(tuple(types))

    def register(self):
        sig = inspect.signature(self.fn)
        # Build a type signature from the method's annotations
        types = [[]]
        for name, parm in sig.parameters.items():
            if name == "self":
                continue
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(
                    f"Argument {name} must be annotated with a type."
                )
            if not (
                isinstance(parm.annotation, type)
                or isinstance(parm.annotation, type(ClassVar[T]))
                or isinstance(parm.annotation, type(TypeVar("T")))
            ):
                raise TypeError(
                    f"""Argument {name} annotation must be a type.
                    It is a {parm.annotation}"""
                )
            if parm.default is not inspect.Parameter.empty:
                for i in types:
                    self._register(tuple(i))

            new = deepcopy(types)

            # append annotation
            for i in types:
                i.append(parm.annotation)

            # append None type
            if (
                parm.default is not inspect.Parameter.empty
                and parm.default is None
            ):
                for i in new:
                    i.append(type(None))
                types += new

        for i in types:
            self._register(tuple(i))

    def key(self, args=None):
        """Returns the key that will uniquely identify
        a function (even when it is overloaded).
        """
        # when register, extract the declare arguments as signature
        # when call, use passed argument as signature
        if args is None:
            return [
                tuple(
                    [
                        self.fn.__module__,
                        self.fn.__class__,
                        self.fn.__name__,
                        sig,
                    ]
                )
                for sig in self.signatures
            ]
        else:
            return [
                tuple(
                    [
                        self.fn.__module__,
                        self.fn.__class__,
                        self.fn.__name__,
                        tuple([type(i) for i in args]),
                    ]
                )
            ]


class Namespace(object):
    """Namespace is the singleton class that is responsible
    for holding all the functions.
    """

    __instance = None

    def __init__(self):
        if self.__instance is None:
            self.function_map = dict()
            Namespace.__instance = self
        else:
            raise Exception("cannot instantiate a virtual Namespace again")

    @staticmethod
    def get_instance():
        if Namespace.__instance is None:
            Namespace()
        return Namespace.__instance

    def register(self, fn):
        """registers the function in the virtual namespace and returns
        an instance of callable Function that wraps the
        function fn.
        """
        func = Function(fn)
        for key in func.key():
            if key in self.function_map:
                continue  # if duplicate, let it go. user's fault.
                raise Exception(
                    f"""duplicate signature:
                                [{self.function_map[key]}]
                                [{key}]
                                """
                )
            self.function_map[key] = fn
        return func

    def get(self, fn, *args):
        """get returns the matching function from the virtual namespace.
        return None if it did not fund any matching function.
        """
        func = Function(fn)
        return self.function_map.get(func.key(args)[0])


def overload(fn):
    """overload is the decorator that wraps the function
    and returns a callable object of type Function.
    """
    return Namespace.get_instance().register(fn)
