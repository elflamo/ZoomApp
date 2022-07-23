from rest_framework.views import APIView
from rest_framework.response import Response
import logging
from main.tasks import handle_queue
from main.models import ZoomToken
import hmac
import hashlib
import base64

logger = logging.getLogger(__name__)

CONTENT_JSON = "application/json"
TOKEN = "d3wGmFeXTl2b49fRoyhtaw"


class CallbackView(APIView):

    def get(self, request):
        return Response(data={"message": "success"}, status=200, content_type=CONTENT_JSON)

    def post(self, request):
        try:
            if request.data["event"] == "endpoint.url_validation":
                sample_file = open("sample.txt", "w")
                sample_file.write("1")
                sample_file.close()
                plain_token = request.data["payload"]["plainToken"]
                digest = hmac.new(
                    TOKEN.encode("utf-8"),
                    msg=plain_token.encode("utf-8"),
                    digestmod=hashlib.sha256).digest()
                signature = base64.b64encode(digest).decode()

                return Response(
                    data={
                        "encryptedToken": signature,
                        "plainToken": plain_token
                    },
                    status=200,
                    content_type=CONTENT_JSON
                )
            else:
                zoom_token = ZoomToken.objects.first().token
                if zoom_token == request.META.get('HTTP_AUTHORIZATION', None):
                    handle_queue.apply_async(
                        args=[request.data], queue="request_queue"
                    )
                    return Response(data={"message": "success"}, status=200, content_type=CONTENT_JSON)
                else:
                    return Response(data={"message": "Incorrect token"}, status=401, content_type=CONTENT_JSON)
        except Exception as exc:
            logger.exception("Exception: {}".format(str(exc)))
            return Response(data={"message": "success"}, status=400, content_type=CONTENT_JSON)
