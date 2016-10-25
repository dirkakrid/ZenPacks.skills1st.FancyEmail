===============================================================================================================
ZenPack to provide new email notification type, FancyEmail, with html formatting, image and custom event fields
===============================================================================================================

Description
===========

ZenPack provides a new Notification type, FancyEmail, which is based on
the standard Email notification but whose body and clear_body contain
html formatting rather than simple text.  Most of the code is in
actions.py with a few "hooks" in configure.zcml.

An image header for emails is provided in imageFile0.jpg.
The default also contains an image for the body and clear_body.  The
images are in imageFile1.jpg and imageFile2.jpg.  Others could be
added as required (the code is commented to help).  You can change the
image simpy by replacing the file - no need to stop and start anything.

The notifications use non-standard event fields to enhance the message,
particularly evt/sevColour, evt/sevBackgroundColour and evt/SevString.  
These fields and other non-standard event fields are generated / checked in 
a top-level event transform supplied in root_transform.txt.  Note that these fields must
be non-null.  They can be the null string but must not be None.

root_transform.txt has a test for a custom property, cCategory.  This property is
not shipped with the ZenPack.  It can be created from the GUI at the top-level device
class.  Note that the default should not be None but can be the null string.  If this
property is not created, the transform defaults evt.Category to "Unknown".
 
Note that the fomatting of the email body and clear body have some very long lines.
You seem to need this, otherwise you get lots of white space at the top of your email.
Different table formats are provided for the body and clear body.

The zep directory of the ZenPack defines the new fields for Category, Site and Region
so that they can be selected as column headers in an Event Console.  In theory, these
new fields should also be available as selection criteria for triggers but, for this
to work, you need bug fixes for ZEN-8391 (search for "Trigger conditions are hard-coded 
in the JS" in Zenoss JIRA), https://jira.zenoss.com/browse/ZEN-8391 .  If the zep.json
file has been changed, you will need to install / reinstall the ZenPack and restart
zenhub, zopectl and zenactiond.

When testing, if you have changed actions.py, remember to bounce zenhub, zopectl (or
zenwebserver for Zenoss Enterprise) and zenactiond.  You must also create a new 
notification of type FancyEmail - an existing one will still have the old html.

This ZenPack has now been tested with Zenoss 5.1.7 where bugs related to shipping both
triggers and notifications have been resolved.  The single trigger includes a Zenpack-shipped
event field.  Three notifications are included:

    * App_Cat_Test_command      disabled by default. Logs to /tmp/skills_zep_test.  Note that, in
       Zenoss 5.x, this file will exist only in the zenactiond container.
    * App_Cat_Test_email        disabled by default.  Sends a standard email with default
       email body and clear body
    * App_Cat_Test_fancyemail   enabled by default.  Sends a fancyemail with the default
       fancyemail html body and clear body

Both email notifications should automatically fill in default email fields such as SMTP host,
useTLS, etc if they are not supplied directly.  This is dependent on having the fix described
in https://jira.zenoss.com/browse/ZEN-15367.

Note that subscribers to both email notifications must be configured locally after installing
the ZenPack.



Requirements & Dependencies
===========================

    * Zenoss Versions Supported: 4.x, 5.x
    * External Dependencies: 
    * ZenPack Dependencies:
    * Installation Notes: Restart zenhub, zopectl and zenactiond after installation
    * Configuration:  Recreate any Notification that uses a FancyEmail type.


Download
========
Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.0+ `Latest Package for Python 2.7`_
* Zenoss 5.0+ `Latest Package for Zenoss 5 Python 2.7`_

ZenPack installation
======================

This ZenPack can be installed from the .egg file using either the GUI or the
zenpack command line but, since it is demonstration code that you are likely to 
want to modify, it is more likely installed in development mode.  From github - 
https://github.com/jcurry/ZenPacks.skills1st.FancyEmail  use the ZIP button
(top left) to download a tgz file and unpack it to a local directory, say,
$ZENHOME/local.  Install from $ZENHOME/local with:

zenpack --link --install ZenPacks.skills1st.FancyEmail

Restart zenhub, zopectl and zenactiond after installation.



Change History
==============
* 1.0.0
   * Initial Release
* 1.1.0
   * Better table formatting and images.  zep file included for 3 event fields
* 1.2.0
   * Updated for Zenoss 5 with trigger and notification bugs fixed

Screenshots
===========
|email1|
|email2|


.. External References Below. Nothing Below This Line Should Be Rendered

.. _Latest Package for Python 2.7: https://github.com/jcurry/ZenPacks.skills1st.FancyEmail/blob/master/dist/ZenPacks.skills1st.FancyEmail-1.1.0-py2.7.egg?raw=True
.. _Latest Package for Zenoss 5 Python 2.7: https://github.com/jcurry/ZenPacks.skills1st.FancyEmail/blob/5.1/dist/ZenPacks.skills1st.FancyEmail-1.2.0-py2.7.egg?raw=True
.. |email1| image:: https://github.com/jcurry/ZenPacks.skills1st.FancyEmail/blob/master/screenshots/FancyEmail_error.jpg
.. |email2| image:: https://github.com/jcurry/ZenPacks.skills1st.FancyEmail/blob/master/screenshots/FancyEmail_clear.jpg

