import abc
class CrawlerBase:
    def __init__(self,config,total_crawled :int =0):
        self.config = config
        self.total_crawled = total_crawled

    @abc.abstractmethod
    def crawl_website(self):
        pass
       