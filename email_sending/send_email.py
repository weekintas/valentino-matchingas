from dotenv import dotenv_values
import requests
import json

from dotenv import dotenv_values

from utils.classes.email_attachment import EmailAttachment
from email_sending.prepare_html_body import get_email_html_body
from utils.constants import (
    ZEPTOMAIL_HEADER_ACCEPT,
    ZEPTOMAIL_HEADER_CONTENT_TYPE,
    ZEPTOMAIL_REQUEST_METHOD,
    ZEPTOMAIL_SERVICE_EMAIL,
    DEFAULT_RESULTS_EMAIL_SUBJECT,
)


def send_result_email(
    to_address: str,
    html_body_filepath: str,
    subject: str = DEFAULT_RESULTS_EMAIL_SUBJECT,
    attachments: list[EmailAttachment] = [],
):
    env_values = dotenv_values(".env")
    html_body = get_email_html_body(html_body_filepath)

    # constructing parts of the email for the ZeptoMail API
    headers = {
        "accept": ZEPTOMAIL_HEADER_ACCEPT,
        "content-type": ZEPTOMAIL_HEADER_CONTENT_TYPE,
        "authorization": env_values["ZEPTOMAIL_API_SEND_MAIL_TOKEN"],
    }

    payload_dict = {
        "from": {
            "address": env_values["EMAIL_FROM_ADDRESS"],
            "name": env_values["EMAIL_FROM_NAME"],
        },
        "to": [{"email_address": {"address": to_address}}],
        "subject": subject,
        "htmlbody": html_body,
        "attachments": [
            {
                "name": attachment.filename,
                "content": attachment.get_base64_content(),
                "mime_type": attachment.type.value,
            }
            for attachment in attachments
        ],
    }
    # print(attachment_content)
    payload = json.dumps(payload_dict)

    # sending the email via the ZeptoMail API
    email_response = requests.request(ZEPTOMAIL_REQUEST_METHOD, ZEPTOMAIL_SERVICE_EMAIL, data=payload, headers=headers)
    return email_response.ok, email_response.status_code, email_response.json()


# a, b = send_result_email(
#     # "guodutebal@gmail.com",
#     # "weekintas@gmail.com",
#     # "majauskaitelorena999@icloud.com",
#     "mylimasv@gmail.com",
#     "_examples/enrollment_confirmation.html",
#     subject="Valentino patvirtinimo testas 6",
#     # attachments=[
#     #     EmailAttachment("_examples/generated_output_files/pdf example.pdf"),
#     #     # EmailAttachment("files_example/plakatas.png", filename="Rezultatai Instagramui"),
#     # ],
# )
# print(a, b["message"], b["request_id"], b)

# {
#   "data": [
#     {
#       "code": "EM_104",
#       "additional_info": [],
#       "message": "Email request received"
#     }
#   ],
#   "message": "OK",
#   "request_id": "13ef.36acb70da80ba20b.m1.1f1790e0-01e6-11f1-94d1-dad70ff08860.19c297920ee",
#   "object": "email"
# }
