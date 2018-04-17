#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from cloudformation.ci_factory import CIFactory
from cloudformation.cf_client import CFClient

def process(task_vars):
    deployed = task_vars['previousDeployed']

    client = CFClient.new_instance(deployed.container)
    template = client.get_template_body(deployed)
    if template is None:
        print 'Template body not found.  Skipping'
        return

    template_metadata = template['Metadata']

    ci_fact = CIFactory.new_instance(repositoryService, metadataService, deployed.outputVariables)

    # process individually to guarantee order
    if 'XLD::Environments' in template_metadata:
        ci_tmpl = template_metadata['XLD::Environments']
        ci_fact.deleteCis('Environments', ci_tmpl)

    if 'XLD::Infrastructure' in template_metadata:
        ci_tmpl = template_metadata['XLD::Infrastructure']
        ci_fact.deleteCis('Infrastructure', ci_tmpl)

    if 'XLD::Applications' in template_metadata:
        ci_tmpl = template_metadata['XLD::Applications']
        ci_fact.deleteCis('Applications', ci_tmpl)

    print "Done"


if __name__ == '__main__' or __name__ == '__builtin__':
    process(locals())
