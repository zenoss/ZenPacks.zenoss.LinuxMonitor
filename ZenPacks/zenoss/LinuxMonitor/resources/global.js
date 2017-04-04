/*##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################*/

var ZC = Ext.ns('Zenoss.component');

Ext.onReady(function(){
    Ext.ComponentMgr.onAvailable('deviceoverviewpanel_customsummary', function(){
        // remove snmpsummary for /Server/SSH/Linux devices
        if (window.location.pathname.indexOf('/Server/SSH/Linux/devices/') != -1){
            try{
                this.remove('deviceoverviewpanel_snmpsummary', false);
            }
            catch(err){
                console.log(err);
            }
        }
    });
});

