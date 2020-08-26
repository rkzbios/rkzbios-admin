#import prepare_settings #@UnusedImport
        
from unittest import TestCase, main       

from django.conf import settings, global_settings



test_defaults={
}

def configure_settings_for_test(additional_settings={}):
    if not settings.configured:
        total_settings = test_defaults
        total_settings.update(**additional_settings)
        settings.configure(global_settings, **total_settings)


configure_settings_for_test(additional_settings={"TEMPLATE_DIRS": "", "INSTALLED_TEMPLATE_APPS":[]})

from kiini.core.jinja import env


class TestIt(TestCase):
    from jimbo_mail.mail_connections import MailGunConnectionSettings
    from persistent.serializer import JsonSerializer
    mg = MailGunConnectionSettings(
        domain='sandboxdcf43d206af14bfea97d9935782f6cc4.mailgun.org',
        privateKey='key-7ecc7c60f368bdef2f5f84fba4145423',
        publicKey='pubkey-cc185b9df1e0a47d3b50be5d24c242f1'
    )
    json = JsonSerializer().serialize(mg)
    print(json)


class TestRules(TestCase):
        
    def testTemplating2Pass(self):


        # We want to use a jinja template so we can see the html, so we must have other tokens that are replaced and
        # then form a jinja template that renders the email
        template = env.from_string("Hallo ${ username }$ {$ for a in list $} ${ a }$ {$ endfor $}")
        context = {"username": "test"}
        template_str = template.render(**context)
        
        #naive implementation for substituting tags
        template_str = template_str.replace("${", "{{")
        template_str = template_str.replace("}$", "}}")
        template_str = template_str.replace("{$", "{%")
        template_str = template_str.replace("$}", "%}")
        
        
        # this final template can be cached!!!!
        final_template = env.from_string(template_str)
        rendered = final_template.render({"username": "roho", "list": ["a","b"]})
        
        self.assertEquals(rendered, u"Hallo roho  a  b ")
        

        
if __name__ == '__main__':
    main() 