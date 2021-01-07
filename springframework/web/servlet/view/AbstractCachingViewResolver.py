from abc import abstractmethod, ABC
import threading
import logging
from collections import OrderedDict

from springframework.utils.mock.inst import Locale
from springframework.web.context.support.WebApplicationObjectSupport import (
    WebApplicationObjectSupport,
)
from springframework.web.servlet import View
from springframework.web.servlet.ViewResolver import ViewResolver


class UnresolvedView(View):
    def get_content_type(self) -> str:
        return None

    def render(self, model: dict, request, response) -> None:
        pass


class CacheFilter:
    def filter(self, view, viewName, locale):
        return True


class AbstractCachingViewResolver(
    WebApplicationObjectSupport, ViewResolver, ABC
):

    # Default maximum number of entries for the view cache: 1024.
    DEFAULT_CACHE_LIMIT = 1024

    lock = threading.Lock()

    _UNRESOLVED_VIEW = UnresolvedView()

    # Default cache filter that always caches.
    # private static final CacheFilter DEFAULT_CACHE_FILTER = (view, viewName, locale) -> true;
    _DEFAULT_CACHE_FILTER = CacheFilter()

    # The maximum number of entries in the cache.
    _cacheLimit = DEFAULT_CACHE_LIMIT

    # Whether we should refrain from resolving views again if unresolved once.
    _cacheUnresolved = True

    # Filter function that determines if view should be cached.
    _cacheFilter = _DEFAULT_CACHE_FILTER

    # Fast access cache for Views, returning already cached instances without a global lock.
    # __viewAccessCache = dict()

    # Map from view key to View instance, synchronized for View creation.
    # __viewCreationCache = my_order_dict()

    def __init__(self):
        super().__init__()

        class my_order_dict(OrderedDict):
            def __setitem__(self, key, value):
                if self.getcache_limit() <= self.__len__():
                    self.popitem(last=False)
                return super().__setitem__(key, value)

            getcache_limit = self.getcache_limit

        self._viewCreationCache = my_order_dict()
        self._viewAccessCache = dict()

    # Specify the maximum number of entries for the view cache.
    # Default is 1024.
    def set_cache_limit(self, cacheLimit: int) -> None:
        self._cacheLimit = cacheLimit

    # Return the maximum number of entries for the view cache.
    def getcache_limit(self) -> int:
        return self._cacheLimit

    # Enable or disable caching.
    # Disable this only for debugging and development.
    def set_cache(self, cache: bool) -> None:
        self._cacheLimit = self.DEFAULT_CACHE_LIMIT if cache else 0

    # Return if caching is enabled.
    def is_cache(self) -> bool:
        return self._cacheLimit > 0

    def set_cache_unresolved(self, cacheUnresolved: bool) -> None:
        self._cacheUnresolved = cacheUnresolved

    # Return if caching of unresolved views is enabled.
    def is_cache_unresolved(self) -> bool:
        return self._cacheUnresolved

    def set_cache_filter(self, cacheFilter: CacheFilter) -> None:
        assert cacheFilter is not None
        self._cacheFilter = cacheFilter

    def get_cache_filter(self) -> CacheFilter:
        return self._cacheFilter

    def resolve_view_name(self, viewName: str, locale: Locale) -> View:
        if not self.is_cache():
            return self.create_view(viewName, locale)

        else:
            cacheKey = self.get_cache_key(viewName, locale)
            view = self._viewAccessCache.get(cacheKey)
            if view is None:
                with self.lock:
                    view = self._viewCreationCache.get(cacheKey)
                    if view is None:
                        # Ask the subclass to create the View object.
                        view = self.create_view(viewName, locale)
                        if view is None and self._cacheUnresolved:
                            view = self._UNRESOLVED_VIEW

                        if view is not None and self._cacheFilter.filter(
                            view, viewName, locale
                        ):
                            self._viewAccessCache[cacheKey] = view
                            self._viewCreationCache[cacheKey] = view

            return view if view != self._UNRESOLVED_VIEW else None

    def _format_key(self, cacheKey: object) -> str:
        return "View with key [" + cacheKey + "] "

    def get_cache_key(self, viewName: str, locale: Locale) -> object:
        return viewName + "_" + locale

    def remove_from_cache(self, viewName: str, locale: Locale) -> None:
        if not self.is_cache():
            logging.warning()
        else:
            cacheKey = self.get_cache_key(viewName, locale)
            with self.lock:
                self._viewAccessCache.pop(cacheKey, None)
                cachedView = self._viewCreationCache.pop(cacheKey, None)

            if cachedView is None:
                logging.debug(f"{cachedView} not found in the cache")
            else:
                logging.debug(f"{cachedView} cleared from cache")

    def clear_cache(self) -> None:
        with self.lock:
            self._viewAccessCache = dict()
            self._viewCreationCache = dict()

    def create_view(self, viewName: str, locale: Locale) -> View:
        return self.load_view(viewName, locale)

    @abstractmethod
    def load_view(self, viewName: str, locale: Locale) -> View:
        raise NotImplementedError
