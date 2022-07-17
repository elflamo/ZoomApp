from rest_framework.views import APIView
from rest_framework.response import Response
import logging
from main.tasks import handle_queue

logger = logging.getLogger(__name__)

CONTENT_JSON = "application/json"


class CallbackView(APIView):

    def get(self, request):
        return Response(data={"message": "success"}, status=200, content_type=CONTENT_JSON)

    def post(self, request):
        try:
            handle_queue.apply_async(
                args=[request.data], queue="request_queue"
            )
            return Response(data={"message": "success"}, status=200, content_type=CONTENT_JSON)
        except Exception as exc:
            logger.exception("Exception: {}".format(str(exc)))
            return Response(data={"message": "success"}, status=400, content_type=CONTENT_JSON)
