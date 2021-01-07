from springframework.web.servlet.view import InternalResourceView
from springframework.utils.mock.inst import JstlUtils


class JstlView(InternalResourceView):
    def __init__(self, url: str = None, messageSource=None):
        super().__init__(self, url)
        self.messageSource = messageSource

    def init_servlet_context(self, servletContext) -> None:
        if self.messageSource is not None:
            self.messageSource = JstlUtils.getJstlAwareMessageSource(
                servletContext, self.messageSource
            )
        super().init_servlet_context(servletContext)

    def expose_helpers(self, request) -> None:
        if self.messageSource is not None:
            JstlUtils.exposeLocalizationContext(request, self.messageSource)
