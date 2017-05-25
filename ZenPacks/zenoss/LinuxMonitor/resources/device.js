Ext.apply(Zenoss.render, {
    zenpacklib_ZenPacks_zenoss_LinuxMonitor_fileSystemStorageDevice: function(obj, metaData, record, rowIndex, colIndex) {
        if (typeof(obj) == "object") {
            return Zenoss.render.zenpacklib_ZenPacks_zenoss_LinuxMonitor_entityLinkFromGrid(obj, metaData, record, rowIndex, colIndex);
        }

        return obj;
    },

    zenpacklib_ZenPacks_zenoss_LinuxMonitor_percentage: function(value) {
        if (value === "Unknown" || value < 0) {
            return _t("Unknown");
        } else {
            return value + "%";
        }
    }
});
