import qrcode
import requests
import shortuuid

from django.conf import settings
from kiini.core.jinja import render_to_string

FORBIDDEN_CHARS = ['L', 'I', 'J', 'O', 'Q', 'B', '0', '1', '2', '8', 'Z']


class MockRequest(object):

    def __init__(self, host):
        self.host = host
        self.LANGUAGE_CODE = 'nl'
        self.META = {"HTTP_HOST": host}

    def get_host(self):
        return self.host


def get_short_code():
    max_tries = 30
    count = 0
    while count < max_tries:
        new_uid = shortuuid.uuid().upper()
        constructed_uid = ""
        for ch in iter(new_uid):
            if ch not in FORBIDDEN_CHARS:
                constructed_uid = constructed_uid + ch
                if len(constructed_uid) == 4:
                    return constructed_uid
        max_tries = max_tries + 1

    return shortuuid.uuid()[:4]


def create_pdf(ticket_id, access_token, local_filename):

    url = settings.PDF_SERVER + "/generate-pdf"
    ticket_pdf_url = "http://rkzbios.nl/printTicket/%s/%s" % (ticket_id, access_token)
    params = {"url": ticket_pdf_url}
    r = requests.get(url, params=params)
    r.raise_for_status()
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


def create_acccess_token():
    return "aaer.erwerwe.werwerwerwe.werwe.234234.234234."



def create_pdf_old(request, templates, ctx):
    fo = render_to_string(templates, ctx, request=request)
    headers = {'Content-type': 'application/xml'}
    url = settings.FOPDF_SERVER + "/fopdf/fop"
    r = requests.post(url, headers=headers, data=fo.encode('utf-8'))

    if r.status_code == 200:
        return r.content
    else:
        raise Exception("error creating pdf")