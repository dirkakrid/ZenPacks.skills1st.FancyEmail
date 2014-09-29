##############################################################################
#
# Author:               Jane Curry
# Date:                 Sep 24th 2014
# Description:           New action to send pretty html email
# Updated:
#
##############################################################################

import logging
import re
import os

from zope.interface import implements

from Products.ZenModel.actions import (
    IActionBase, _signalToContextDict, processTalSource, TargetableAction)
from Products.ZenModel.interfaces import IAction
from Products.ZenUtils.guid.guid import GUIDManager
from Products.Zuul.interfaces import IInfo
from Products.ZenModel.interfaces import IProvidesEmailAddresses
from Products.Zuul.infos import InfoBase
from Products.Zuul.infos.actions import ActionFieldProperty
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t
from zope.schema.vocabulary import SimpleVocabulary
import textwrap
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate
from Products.ZenUtils.Utils import sendEmail


log = logging.getLogger("zen.actions.FancyEmail")

def getNotificationBodyTypes():
    return ['html', 'text']

class ActionExecutionException(Exception): pass

class IFancyEmailActionContentInfo(IInfo):
    body_content_type = schema.Choice(
        title       = _t(u'Body Content Type'),
        vocabulary  = SimpleVocabulary.fromValues(getNotificationBodyTypes()),
        description = _t(u'The content type of the body for emails.'),
        default     = u'html'
    )

    subject_format = schema.TextLine(
        title       = _t(u'Message (Subject) Format'),
        description = _t(u'The template for the subject for emails.'),
        default     = _t(u'[Z] ${evt/device} ${evt/summary}')
    )

    # body_format includes the following event fields which MUST exist and be non-null:
    # Standard fields
    # evt/device , evt/ipAddress , evt/count , evt/summary , evt/component , evt/eventClass , 
    #     evt/firstTime , evt/lastTime , evt/message
    # Customised fields created in a root-level event transform - see root_transform.txt
    # evt/utcTime , evt/sevColour , evt/SevString , evt/Category , evt/Site , evt/explanation , evt/resolution
    #  The  evt/sevColour , evt/SevString fields are used by the notification to output text values for
    #     severity (Critical, Error, etc) and to colour-code this string.
    #
    # Any image files are found in this directory.  The "image1" in the <br><img src="cid:image1"><br> line
    #  MUST match the "image1" in msgImage.add_header('Content-ID', '<image1>') in the executeBatch function.
    #   and the same for "image2" in the clear_body_format


    body_format = schema.Text(
        title       = _t(u'Body Format'),
        description = _t(u'The template for the body for emails.'),
        default     = textwrap.dedent(text = u'''
    <b><u> <font size="4" color="Red"><span style="text-transform: uppercase">Zenoss Issue</span></font></u> </b>

    Device: <b> <font size="3" color="Blue"><span style="text-transform: uppercase"> ${evt/device}</span></font> </b>&nbsp&nbsp IP Address:<b> <font size="3" color="Blue"> ${evt/ipAddress} </font> </b>&nbsp&nbsp UTC Time:  <b> <font size="3" color="Blue">${evt/utcTime} </font> </b> &nbsp&nbsp Count:  <b> <font size="3" color="Blue"> ${evt/count} </font> </b> &nbsp&nbsp  Severity:  <b> <font size="3" color=${evt/sevColour}> ${evt/SevString} </font> </b> &nbsp&nbsp Category: <b> <font size="3" color="Blue">${evt/Category}</font> </b>

    Summary: <b> <font size="3" color="Blue">${evt/summary}</font> </b>

    Component: <b> <font size="3" color="Blue"> ${evt/component}</font> </b>
    Site: <b> <font size="3" color="Blue">${evt/Site}</font> </b>
    Explanation:  <b> <font size="3" color="Blue">${evt/explanation}</font> </b>
    Resolution: <b> <font size="3" color="Blue">${evt/resolution}</font> </b>
    Event Class: <b> <font size="3" color="Blue">${evt/eventClass}</font> </b>
    First Time: <b> <font size="3" color="Blue">${evt/firstTime}</font> </b>
    Last Time: <b> <font size="3" color="Blue">${evt/lastTime}</font> </b>

    Message:  ${evt/message}

    <br><img src="cid:image1"><br>
        ''')
    )
    clear_subject_format = schema.TextLine(
        title       = _t(u'Clear Message (Subject) Format'),
        description = _t(u'The template for the subject for CLEAR emails.'),
        default     = _t(u'[Z] CLEAR: ${evt/device} ${clearEvt/summary}')
    )

    clear_body_format = schema.Text(
        title       = _t(u'Body Format'),
        description = _t(u'The template for the body for CLEAR emails.'),
        default     = textwrap.dedent(text = u'''
    <b><u> <font size="4" color="Green"><span style="text-transform: uppercase">Zenoss Issue Cleared</span></font></u> </b>

    Device: <b> <font size="3" color="Blue"><span style="text-transform: uppercase"> ${evt/device}</span></font> </b>&nbsp&nbsp IP Address:<b> <font size="3" color="Blue"> ${evt/ipAddress} </font> </b>&nbsp&nbsp UTC Time:  <b> <font size="3" color="Blue">${evt/utcTime} </font> </b> &nbsp&nbsp Count:  <b> <font size="3" color="Blue"> ${evt/count} </font> </b> &nbsp&nbsp  Severity:  <b> <font size="3" color=${evt/sevColour}> ${evt/SevString} </font> </b> &nbsp&nbsp Category: <b> <font size="3" color="Blue">${evt/Category}</font> </b>

    Summary: <b> <font size="3" color="Blue">${evt/summary}</font> </b>

    Component: <b> <font size="3" color="Blue"> ${evt/component}</font> </b>
    Site: <b> <font size="3" color="Blue">${evt/Site}</font> </b>
    Explanation:  <b> <font size="3" color="Blue">${evt/explanation}</font> </b>
    Resolution: <b> <font size="3" color="Blue">${evt/resolution}</font> </b>
    Event Class: <b> <font size="3" color="Blue">${evt/eventClass}</font> </b>
    First Time: <b> <font size="3" color="Blue">${evt/firstTime}</font> </b>
    Last Time: <b> <font size="3" color="Blue">${evt/lastTime}</font> </b>

    Message:  ${evt/message}

    <a href="${urls/reopenUrl}">Reopen</a>

    <br><img src="cid:image2"><br>

    ''')
    )

    email_from = schema.Text(
        title       = _t(u'From Address for Emails'),
        description = _t(u'The user from which the e-mail originated on the Zenoss server.'),
    )

    host = schema.Text(
        title       = _t(u'SMTP Host'),
        description = _t(u'Simple Mail Transport Protocol (aka E-mail server).'),
    )
    port = schema.Int(
        title       = _t(u'SMTP Port (usually 25)'),
        description = _t(u'TCP/IP port to access Simple Mail Transport Protocol (aka E-mail server).'),
    )

    useTls = schema.Bool(
        title       = _t(u'Use TLS?'),
        description = _t(u'Use Transport Layer Security for E-mail?')
    )

    user = schema.Text(
        title       = _t(u'SMTP Username (blank for none)'),
        description = _t(u'Use this only if authentication is required.'),
    )

    password = schema.Password(
        title       = _t(u'SMTP Password (blank for none)'),
        description = _t(u'Use this only if authentication is required.'),
    )

class FancyEmailActionContentInfo(InfoBase):
    implements(IFancyEmailActionContentInfo)

    body_content_type = ActionFieldProperty(IFancyEmailActionContentInfo, 'body_content_type')
    subject_format = ActionFieldProperty(IFancyEmailActionContentInfo,'subject_format')
    body_format = ActionFieldProperty(IFancyEmailActionContentInfo, 'body_format')
    clear_subject_format = ActionFieldProperty(IFancyEmailActionContentInfo, 'clear_subject_format')
    clear_body_format = ActionFieldProperty(IFancyEmailActionContentInfo, 'clear_body_format')
    email_from = ActionFieldProperty(IFancyEmailActionContentInfo, 'email_from')
    host = ActionFieldProperty(IFancyEmailActionContentInfo, 'host')
    port = ActionFieldProperty(IFancyEmailActionContentInfo, 'port')
    useTls = ActionFieldProperty(IFancyEmailActionContentInfo, 'useTls')
    user = ActionFieldProperty(IFancyEmailActionContentInfo, 'user')
    password = ActionFieldProperty(IFancyEmailActionContentInfo, 'password')

class FancyEmailAction(IActionBase, TargetableAction):
    """
    Derived class to execute an arbitrary command on a remote windows machine
    when a notification is triggered.
    """
    implements(IAction)

    id = 'fancyemail'
    name = 'FancyEmail'
    actionContentInfo = IFancyEmailActionContentInfo

    shouldExecuteInBatch = True

    def __init__(self):
        super(FancyEmailAction, self).__init__()

    def getDefaultData(self, dmd):
        return dict(host=dmd.smtpHost,
                    port=dmd.smtpPort,
                    user=dmd.smtpUser,
                    password=dmd.smtpPass,
                    useTls=dmd.smtpUseTLS,
                    email_from=dmd.getEmailFrom())

    def setupAction(self, dmd):
        self.guidManager = GUIDManager(dmd)

    def executeBatch(self, notification, signal, targets):
        log.debug("Executing %s action for targets: %s", self.name, targets)
        self.setupAction(notification.dmd)

        data = _signalToContextDict(signal, self.options.get('zopeurl'), notification, self.guidManager)
        if signal.clear:
            log.debug('This is a clearing signal.')
            subject = processTalSource(notification.content['clear_subject_format'], **data)
            body = processTalSource(notification.content['clear_body_format'], **data)
        else:
            subject = processTalSource(notification.content['subject_format'], **data)
            body = processTalSource(notification.content['body_format'], **data)

        log.debug('Sending this subject: %s' % subject)
        log.debug('Sending this body: %s' % body)

        plain_body = MIMEText(self._stripTags(body))
        email_message = plain_body

        if notification.content['body_content_type'] == 'html':
            email_message = MIMEMultipart('related')
            email_message_alternative = MIMEMultipart('alternative')
            email_message_alternative.attach(plain_body)

            html_body = MIMEText(body.replace('\n', '<br />\n'))
            html_body.set_type('text/html')
            email_message_alternative.attach(html_body)

            email_message.attach(email_message_alternative)

            # Attach image

            (zpdir, tail) = os.path.split(__file__)   # Get path to this directory
            if signal.clear:
                imFile = zpdir + '/imageFile2.jpg'
                imageFile = open(imFile, 'rb')
                msgImage = MIMEImage(imageFile.read())
                imageFile.close()
                msgImage.add_header('Content-ID', '<image2>')
                email_message.attach(msgImage)
            else:
                imFile = zpdir + '/imageFile1.jpg'
                imageFile = open(imFile, 'rb')
                msgImage = MIMEImage(imageFile.read())
                imageFile.close()
                msgImage.add_header('Content-ID', '<image1>')
                email_message.attach(msgImage)



        host = notification.content['host']
        port = notification.content['port']
        user = notification.content['user']
        password = notification.content['password']
        useTls = notification.content['useTls']
        email_from = notification.content['email_from']

        email_message['Subject'] = subject
        email_message['From'] = email_from
        email_message['To'] = ','.join(targets)
        email_message['Date'] = formatdate(None, True)

        result, errorMsg = sendEmail(
            email_message,
            host, port,
            useTls,
            user, password
        )

        if result:
            log.debug("Notification '%s' sent emails to: %s",
                     notification.id, targets)
        else:
            raise ActionExecutionException(
                "Notification '%s' FAILED to send emails to %s: %s" %
                (notification.id, targets, errorMsg)
            )

    def getActionableTargets(self, target):
        """
        @param target: This is an object that implements the IProvidesEmailAddresses
            interface.
        @type target: UserSettings or GroupSettings.
        """
        if IProvidesEmailAddresses.providedBy(target):
            return target.getEmailAddresses()

    def _stripTags(self, data):
        """A quick html => plaintext converter
           that retains and displays anchor hrefs

           stolen from the old zenactions.
           @todo: needs to be updated for the new data structure?
        """
        tags = re.compile(r'<(.|\n)+?>', re.I | re.M)
        aattrs = re.compile(r'<a(.|\n)+?href=["\']([^"\']*)[^>]*?>([^<>]*?)</a>', re.I | re.M)
        anchors = re.finditer(aattrs, data)
        for x in anchors: data = data.replace(x.group(), "%s: %s" % (x.groups()[2], x.groups()[1]))
        data = re.sub(tags, '', data)
        return data

    def updateContent(self, content=None, data=None):
        updates = dict()
        updates['body_content_type'] = data.get('body_content_type', 'html')

        properties = ['subject_format', 'body_format', 'clear_subject_format', 'clear_body_format']
        properties.extend(['host', 'port', 'user', 'password', 'useTls', 'email_from'])
        for k in properties:
            updates[k] = data.get(k)

        content.update(updates)


