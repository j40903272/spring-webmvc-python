from springframework.web.servlet.View import View


class SmartView(View):
    def isRedirectView(self):
        raise NotImplementedError
