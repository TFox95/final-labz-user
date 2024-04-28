
from fastapi import APIRouter
from core.config import settings
from sendgrid.helpers.mail import Mail, HtmlContent
from jinja2 import Template

from emailManager.html_templates import basic_email_template
from emailManager.schemas import job_form_schema

router = APIRouter(
    prefix="/emailManager"
)


@router.get("/")
def get_auth():
    return "app/auth app created!"


@router.post("/submit")
async def send_email(payload: job_form_schema):

    temp = Template(basic_email_template)
    html_content = temp.render(firstName=payload.firstName,
                               lastName=payload.lastName,
                               companyName=payload.companyName,
                               businessEmail=payload.bussinessEmail,
                               phoneNumber=payload.phoneNumber,
                               description=payload.description)
    msg = Mail(from_email="hgamab12@gmail.com",
               to_emails="TFox95@aol.com",
               subject="Potential IT Client: Inbound",
               html_content=HtmlContent(html_content))

    client = await settings.SENDGRID_CLIENT()

    response = client.send(msg)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return "200"

