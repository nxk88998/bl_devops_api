from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkecs.v2 import *


class HuaweiCloud():
    def __init__(self,ak,sk):
        # self.ak = "CODZ9HNDCSYZZK0SWVEL"
        # self.sk = "TVaXj6e0UbX9Qol6KQgWgnZNNCyAQUeGKSdhizwe"
        self.ak = ak
        self.sk = sk

#区域列表查询

if __name__ == "__main__":
    ak = "CODZ9HNDCSYZZK0SWVEL"
    sk = "TVaXj6e0UbX9Qol6KQgWgnZNNCyAQUeGKSdhizwe"

    credentials = BasicCredentials(ak, sk) \

    client = EcsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(EcsRegion.value_of("cn-east-3")) \
        .build()

    try:
        request = NovaListAvailabilityZonesRequest()
        response = client.nova_list_availability_zones(request)
        print(response)
    except exceptions.ClientRequestException as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error_code)
        print(e.error_msg)




# if __name__ == "__main__":
#     ak = "CODZ9HNDCSYZZK0SWVEL"
#     sk = "TVaXj6e0UbX9Qol6KQgWgnZNNCyAQUeGKSdhizwe"
#
#     credentials = BasicCredentials(ak, sk) \
#
#     client = EcsClient.new_builder() \
#         .with_credentials(credentials) \
#         .with_region(EcsRegion.value_of("cn-east-2")) \
#         .build()
#
#     try:
#         request = ShowServerRequest()
#         request.server_id = "88f0c6fd-f22a-4ea7-a4de-7bf28e582415"
#         response = client.show_server(request)
#
#         print(response)
#     except exceptions.ClientRequestException as e:
#         print(e.status_code)
#         print(e.request_id)
#         print(e.error_code)
#         print(e.error_msg)
