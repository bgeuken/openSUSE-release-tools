#
# (C) 2013 coolo@suse.de, openSUSE.org
# Distribute under GPLv2 or GPLv3
#
# Copy this script to ~/.osc-plugins/ or /var/lib/osc-plugins .
# Then try to run 'osc checker --help' to see the usage.

from xml.etree import cElementTree as ET
from osc.core import change_request_state
from osc.core import get_dependson
from osc.core import http_GET
from osc.core import makeurl

def _checker_check_dups(self, project, opts):
    url = makeurl(opts.apiurl, ['request'], "states=new,review&project=%s&view=collection" % project)
    f = http_GET(url)
    root = ET.parse(f).getroot()
    rqs = {}
    for rq in root.findall('request'):
        id = rq.attrib['id']
        for a in rq.findall('action'):
            source = a.find('source')
            target = a.find('target')
            type = a.attrib['type']
            assert target != None
            if target.attrib['project'] != project:
                continue
            # print(id)
            # ET.dump(target)
            if 'package' not in target.attrib:
                continue
            package = target.attrib['package']
            if type + package in rqs:
                [oldid, oldsource] = rqs[type + package]
                if oldid > id:
                    s = oldid
                    oldid = id
                    id = s
                assert oldid < id
                if source != None and oldsource != None:
                    if (source.attrib['project'] == oldsource.attrib['project'] and
                       source.attrib['package'] == oldsource.attrib['package']):
                        change_request_state(opts.apiurl, str(oldid), 'superseded',
                                     'superseded by %s' % id, id)
                        continue
                print("DUPS found:", id, oldid)
            rqs[type + package] = [id, source]


def do_check_dups(self, subcmd, opts, *args):
    """${cmd_name}: checker review of submit requests.

    Usage:
      osc check_dups [OPT] [list] [FILTER|PACKAGE_SRC]
           Shows pending review requests and their current state.

    ${cmd_option_list}
    """

    opts.apiurl = self.get_api_url()

    for p in args[:]:
        self._checker_check_dups(p, opts)

#Local Variables:
#mode: python
#py-indent-offset: 4
#tab-width: 8
#End:
