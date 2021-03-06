import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from core.models import Service,User,CoarseTenant
from services.vaosservice.models import VaosService

from xosresource import XOSResource


class XOSVaosService(XOSResource):
    provides = "tosca.nodes.VaosService"
    xos_model = VaosService
    # copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "private_key_fn", "versionNumber",
    #                 "service_message"]
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "private_key_fn", "versionNumber"]

    def postprocess(self, obj):
        for provider_service_name in self.get_requirements("tosca.relationships.TenantOfService"):
            provider_service = self.get_xos_object(VaosService, name=provider_service_name)

            existing_tenancy = CoarseTenant.get_tenant_objects().filter(provider_service = provider_service, subscriber_service = obj)
            if existing_tenancy:
                self.info("Tenancy relationship from %s to %s already exists" % (str(obj), str(provider_service)))
            else:
                tenancy = CoarseTenant(provider_service = provider_service,
                                       subscriber_service = obj)
                tenancy.save()

                self.info("Created Tenancy relationship  from %s to %s" % (str(obj), str(provider_service)))

    def can_delete(self, obj):
        if obj.slices.exists():
            self.info("Service %s has active slices; skipping delete" % obj.name)
            return False
        return super(XOSVaosService, self).can_delete(obj)

