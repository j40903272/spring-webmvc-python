import xml.etree.ElementTree as ET
import importlib


class MockXmlParser:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.root = ET.parse(xml_path).getroot()
        self.namespace = self._get_namespace()
        self.class_ = self._get_bean_instance()

    def _get_namespace(self):
        ns = dict(
            [
                node
                for (_, node) in ET.iterparse(
                    self.xml_path, events=["start-ns"]
                )
            ]
        )
        ns["_default"] = ns[""]
        del ns[""]
        return ns

    def _get_bean_instance(self):
        # singleton instance
        bean_instance = {}
        for child in self.root:
            try:
                moduleName = child.attrib["class"]
                className = moduleName.split(".")[-1]
                module = importlib.import_module(moduleName)
                class_ = getattr(module, className)
                instance = class_()
                if className not in bean_instance:
                    bean_instance[className] = instance

                id_ = child.attrib["id"]
                if id_ not in bean_instance:
                    bean_instance[id_] = instance
                else:
                    assert "id must be unique"

            except Exception:
                pass

        return bean_instance

    def get_class_by_name(self, name):
        if name in self.class_:
            return self.class_[name]
        else:
            return None

    def get_url_map(self):
        url_map = {}
        simpleUrlHandlerMapping = self.root.find(
            "_default:bean[@class='springframework.web.servlet.handler.SimpleUrlHandlerMapping']",
            namespaces=self.namespace,
        )

        props = simpleUrlHandlerMapping.find(
            "_default:property[@name='mappings']/_default:props",
            namespaces=self.namespace,
        )
        for prop in props:
            routePath = prop.attrib["key"]
            mappedHandlerId = prop.text
            try:
                url_map[routePath] = self.class_[mappedHandlerId]
            except Exception:
                print(f"{mappedHandlerId} isn't found in {self.xml_path}")
        return url_map

    def get_view_resolver_attr(self):
        ret = {}
        properties = self.root.findall(
            "_default:bean[@class='springframework.web.servlet.view.InternalResourceViewResolver']/_default:property",
            namespaces=self.namespace,
        )
        for prop in properties:
            key = prop.attrib["name"]
            value = prop.attrib["value"]
            ret[key] = value
        return ret


if __name__ == "__main__":
    mockXmlParser = MockXmlParser(
        "../../../../tests/web/servlet/myservlet.xml"
    )
    # ../../../../../spring-webmvc-demo/HelloSpring/web/WEB-INF/mvc-servlet.xml
    print(mockXmlParser.get_url_map())
    print(mockXmlParser.get_view_resolver_attr())
    print(mockXmlParser.get_class_by_name("SimpleUrlHandlerMapping"))
    print(mockXmlParser.get_class_by_name("SimpleControllerHandlerAdapter"))
    print(mockXmlParser.get_class_by_name("InternalResourceViewResolver"))
