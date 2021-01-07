import logging
from springframework.web.servlet.view.AbstractUrlBasedView import (
    AbstractUrlBasedView,
)


class InternalResourceView(AbstractUrlBasedView):
    alwaysInclude = False
    preventDispatchLoop = False

    def __init__(self, url: str = None, alwaysInclude: bool = False) -> None:
        super().__init__(url)
        self.alwaysInclude = alwaysInclude

    def set_always_include(self, alwaysInclude: bool) -> None:
        self.alwaysInclude = alwaysInclude

    def set_prevent_dispatch_loop(self, preventDispatchLoop: bool):
        self.preventDispatchLoop = preventDispatchLoop

    def is_context_required(self) -> bool:
        return False

    def render_merged_output_model(
        self, model: dict, request, response
    ) -> None:
        # Expose the model object as request attributes.
        self.expose_model_as_request_attributes(model, request)

        # Expose helpers as request attributes, if any.
        self.expose_helpers(request)

        # Determine the path for the request dispatcher.
        dispatcherPath: str = self.prepare_for_rendering(request, response)

        # Obtain a RequestDispatcher for the target resource (typically a JSP).
        # TODO: use mock
        # rd type: RequestDispatcher
        rd = self.get_request_dispatcher(request, dispatcherPath)
        if rd is None:
            raise ValueError(
                f"""Could not get RequestDispatcher for [{self.get_url()}
            ]: Check that the corresponding file exists within your web application archive!"""
            )

        # If already included or response already committed, perform include, else forward.
        if self.use_include(request, response):
            response.set_content_type(self.get_content_type())
            logging.debug("Including [" + self.get_url() + "]")
            rd.include(request, response)
        else:
            # Note: The forwarded resource is supposed to determine the content type itself.
            logging.debug("Forwarding to [" + self.get_url() + "]")
            rd.forward(request, response)

    def expose_helpers(self, request) -> None:
        pass

    def prepare_for_rendering(self, request, response) -> str:
        path: str = self.get_url()
        assert path is not None, "'url' not set"

        if self.preventDispatchLoop:
            uri: str = request.get_request_uri()
            if path.startswith("/"):
                state = uri == path
            else:
                # TODO: ignore
                # state = uri.equals(StringUtils.applyRelativePath(uri, path))
                state = False
            if state:
                msg = f"""Circular view path [ {path} ]: would dispatch back
                        to the current handler URL [ {uri} ] again. Check your
                        ViewResolver setup! (Hint: This may be the result of an
                        unspecified view, due to default view name generation.)
                        """
                raise ValueError(msg)
        return path

    # return type: RequestDispatcher
    def get_request_dispatcher(self, request, path: str):
        return request.get_request_dispatcher(path)

    def use_include(self, request, response) -> bool:
        # TODO : WebUtils need handle
        # or WebUtils.isIncludeRequest(request)
        return self.alwaysInclude or response.is_committed()
