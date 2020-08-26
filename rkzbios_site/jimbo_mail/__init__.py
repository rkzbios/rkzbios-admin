
class MockRequest(object):
    
    def __init__(self, site):
        self.site = site
        self.LANGUAGE_CODE = 'nl'
        self.META = { "HTTP_HOST": site.domain}
        
    def get_host(self):
        return self.site.domain