import grpc
from grpc import UnaryUnaryClientInterceptor, ClientCallDetails

class AccessTokenAuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, access_token):
        self.access_token = access_token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append(("authorization", f"Bearer {self.access_token}"))
        client_call_details = client_call_details._replace(
            metadata=metadata, credentials=client_call_details.credentials, wait_for_ready=client_call_details.wait_for_ready, timeout=client_call_details.timeout, compression=client_call_details.compression)
        return continuation(client_call_details, request)
