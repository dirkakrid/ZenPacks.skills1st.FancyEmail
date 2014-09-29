===============================================================================================================
ZenPack to provide new email notification type, FancyEmail, with html formatting, image and custom event fields
===============================================================================================================

Description
===========

ZenPack provides a new Notification type, FancyEmail, which is based on
the standard Email notification but whose body and clear_body contain
html formatting rather than simple text.  Most of the code is in
actions.py with a few "hooks" in configure.zcml.

The default also contains an image for the body and clear_body.  The
images are in imageFile1.jpg and imageFile2.jpg.  Others could be
added as required (the code is commented to help).  You can change the
image simpy by replacing the file - no need to stop and start anything.

The notifications use non-standard event fields to enhance the message,
particularly evt/sevColour and evt/SevString.  These fields and other
non-standard event fields are generated / checked in a top-level event
transform supplied in root_transform.txt.  Note that these fields must
be non-null.  They can be the null string but must not be None.

Requirements & Dependencies
===========================

    * Zenoss Versions Supported: 4.x
    * External Dependencies: 
    * ZenPack Dependencies:
    * Installation Notes: Restart zenhub, zopectl and zenactiond after installation
    * Configuration:  Recreate any Notification that uses a FancyEmail type.


Download
========
Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.0+ `Latest Package for Python 2.7`_

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

Screenshots
===========

.. External References Below. Nothing Below This Line Should Be Rendered

.. _Latest Package for Python 2.7: https://github.com/jcurry/ZenPacks.skills1st.FancyEmail/blob/master/dist/ZenPacks.skills1st.FancyEmail-1.0.0-py2.7.egg?raw=True

