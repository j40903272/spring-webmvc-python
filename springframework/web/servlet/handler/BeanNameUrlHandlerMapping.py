from springframework.web.servlet.handler import (
    AbstractDetectingUrlHandlerMapping,
)


class BeanNameUrlHandlerMapping(AbstractDetectingUrlHandlerMapping):
    def determineUrlsForHandler(self, beanName: str) -> list:
        urls = list()
        if beanName.startswith("/"):
            urls.append(beanName)
        aliases: list = self.obtainApplicationContext().getAliases(beanName)
        for alias in aliases:
            if alias.startswith("/"):
                urls.append(alias)
        urls = [str(i) for i in urls]
