/*##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################*/

var ZC = Ext.ns('Zenoss.component');

Ext.apply(Zenoss.render, {
    linux_entityLinkFromGrid: function(obj, col, record) {
        if (!obj)
            return;

        if (obj.name == 'NONE')
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid'){
            if (this.subComponentGridPanel || this.componentType != obj.meta_type)
                isLink = true;
        } else {
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="'+obj.uid+'" onClick="Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\''+obj.uid +'\', \''+obj.meta_type+'\');return false;">'+obj.title+'</a>';            
        } else {
            return obj.title;
        }
    },

});


Ext.define("Zenoss.component.LinuxFileSystemPanel", {
    alias:['widget.LinuxFileSystemPanel'],
    extend:"Zenoss.component.ComponentGridPanel",
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'mount',
            componentType: 'LinuxFileSystem',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'mount'},
                {name: 'storageDevice'},
                {name: 'totalBytes'},
                {name: 'availableBytes'},
                {name: 'usedBytes'},
                {name: 'capacityBytes'},
                {name: 'logicalvolume'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 60
            },{
                id: 'mount',
                dataIndex: 'mount',
                header: _t('Mount Point')
            },{
                id: 'storageDevice',
                dataIndex: 'storageDevice',
                header: _t('Storage Device')
            },{
                id: 'logicalvolume',
                dataIndex: 'logicalvolume',
                header: _t('Logical Volume'),
                renderer: Zenoss.render.linux_entityLinkFromGrid
            },{
                id: 'totalBytes',
                dataIndex: 'totalBytes',
                header: _t('Total Bytes'),
                renderer: Zenoss.render.bytesString
            },{
                id: 'usedBytes',
                dataIndex: 'usedBytes',
                header: _t('Used Bytes'),
                renderer: Zenoss.render.bytesString
            },{
                id: 'availableBytes',
                dataIndex: 'availableBytes',
                header: _t('Free Bytes'),
                renderer: function(n){
                    if (n<0) {
                        return _t('Unknown');
                    } else {
                        return Zenoss.render.bytesString(n);
                    }

                }
            },{
                id: 'capacityBytes',
                dataIndex: 'capacityBytes',
                header: _t('% Util'),
                renderer: function(n) {
                    if (n==='unknown' || n<0) {
                        return _t('Unknown');
                    } else {
                        return n + '%';
                    }
                }

            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons
            }]
        });
        ZC.LinuxFileSystemPanel.superclass.constructor.call(this, config);
    }
});


ZC.registerName('LinuxFileSystem', _t('File System'), _t('File Systems'));
