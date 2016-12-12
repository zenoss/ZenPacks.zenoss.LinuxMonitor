Ext.apply(Zenoss.render, {
    zenpacklib_ZenPacks_zenoss_LinuxMonitor_fileSystemStorageDevice: function(obj, metaData, record, rowIndex, colIndex) {
        if (typeof(obj) == "object") {
            return Zenoss.render.zenpacklib_ZenPacks_zenoss_LinuxMonitor_entityLinkFromGrid(obj, metaData, record, rowIndex, colIndex);
        }

        return obj;
    }
});
