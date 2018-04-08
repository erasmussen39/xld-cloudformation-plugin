#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from com.xebialabs.deployit.plugin.api.reflect import Type

class CIFactory(object):
    def __init__(self, repositoryService, metadataService, root, template, cfout):
        self.repositoryService = repositoryService
        self.metadataService = metadataService 
        self.root = root
        self.template = template
        self.cfout = cfout

    @staticmethod
    def new_instance(repositoryService, metadataService, root, template, cfout):
        return CIFactory(repositoryService, metadataService, root, template, cfout)

    def createCis(self):
        print "Creating configuration items in '%s'" % self.root

        # iterate over list of ci definitions in template
        for ci_info in self.template:
            # scan template for property placeholders, substitute values
            for k in ci_info:
                if '{' in ci_info[k]:
                    try:
                        ci_info[k] = ci_info[k].format(self.cfout)
                    except KeyError:
                        print "WARN: Property placeholder '%s' was not found in the output dictionary." % k

            self._create_ci(ci_info)


    # INTERNAL FUNCTIONS -----------------------------------------

    def _create_ci(self, ci_info):
        print "Creating '%s' : '%s'" % (ci_info['type'], ci_info['id'])

        id = "%s/%s" % (self.root, ci_info['id'])
        if self.repositoryService.exists(id):
            print "CI '%s' already exists, skipping." % id
            return

        type_obj = Type.valueOf(ci_info['type'])
        ci_obj = self.metadataService.findDescriptor(type_obj).newInstance(id)

        # populate ci
        for prop in ci_info:
            if prop in ['id', 'type']:
                continue
            ci_obj.setProperty(prop, ci_info[prop])

        # add ci to repository
        self.repositoryService.create(id, ci_obj)

